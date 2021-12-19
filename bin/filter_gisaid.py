#!/usr/bin/env python
import logging
import re
import sys
import tarfile
from pathlib import Path
from typing import Iterator, Tuple, Optional, IO, Set, Dict, Any

import numpy as np
import pandas as pd
import typer
from Bio.SeqIO.FastaIO import SimpleFastaParser
from rich.console import Console
from rich.logging import RichHandler


def main(
        user_fasta: Path,
        gisaid_fasta: Path,
        gisaid_tsv: Path,
        pangolin_report: Path,
        min_length: int = typer.Option(28000, help='Minimum length for GISAID sequences'),
        max_length: int = typer.Option(31000, help='Maximum length for GISAID sequences'),
        max_ambig: int = typer.Option(3000, help='Max number of ambiguous base sites in GISAID sequences allowed'),
        max_gisaid_seqs: int = typer.Option(100000, help='Max number of filtered GISAID sequences. '
                                                         'If greater than this number, sequences '
                                                         'will be randomly sampled'),
        country: str = typer.Option(None, help='If specified, filter for GISAID sequences '
                                               'belonging to this country.'),
        region: str = typer.Option(None, help='If specified, filter for GISAID sequences '
                                              'belonging to this geographical region.'),
        date_start: str = typer.Option(None,
                                       help='Filter for sequences collected starting on this date. Must be ISO format date (YY-mm-dd), e.g. 2021-12-13'),
        date_end: str = typer.Option(None,
                                     help='Filter for sequences collected until this date. Must be ISO format date (YY-mm-dd), e.g. 2021-12-13'),
        pangolin_lineages: str = typer.Option(None, help='Comma-delimited list of additional Pangolin lineages to '
                                                         'filter for (e.g. "AY.44,AY.43,AY.4,AY.25"'),
        fasta_output: Path = typer.Option(Path('gisaid_sequences.filtered.fasta'),
                                          help='Filtered GISAID sequences.'),
        filtered_metadata: Path = typer.Option(Path('gisaid_metadata.filtered.tsv'),
                                               help='Filtered GISAID metadata table.'),
        nextstrain_metadata: Path = typer.Option(Path('gisaid_metadata.nextstrain.tsv'),
                                                 help='Filtered GISAID metadata table for Nextstrain analysis.'),
        statistics_output: Path = typer.Option(Path('gisaid_stats.json'),
                                               help='GISAID filtering stats.')
):
    init_logging()
    df_pangolin = pd.read_csv(pangolin_report, dtype=str)
    df_pangolin.set_index(df_pangolin.columns[0], inplace=True)
    sample_lineages = set(df_pangolin['lineage'])
    if 'None' in sample_lineages:
        sample_lineages.remove('None')
    logging.info(f'{len(sample_lineages)} unique Pangolin lineages for user sequences: {sample_lineages}')
    df_gisaid = read_gisaid_metadata(gisaid_tsv)
    logging.info(f'Read GISAID metadata table from "{gisaid_tsv}"; '
                 f'{df_gisaid.shape[0]} rows and {df_gisaid.shape[1]} columns')
    gisaid_lineages = df_gisaid['Pango_lineage']
    if pangolin_lineages:
        pangolin_lineages = set(pangolin_lineages.split(','))
        logging.info(f'Filtering for specified Pangolin lineages: {pangolin_lineages}')
        sample_lineages |= pangolin_lineages
    mask: pd.Series = gisaid_lineages.isin(sample_lineages)
    n_gisaid_matching_lineage = int(mask.sum())
    logging.info(f'{n_gisaid_matching_lineage} GISAID sequences matching lineages: {sample_lineages}')
    if date_start:
        dt_start: pd.Timestamp = pd.to_datetime(date_start, errors='coerce')
        if not pd.isna(dt_start):
            collection_datetimes: pd.Series = pd.to_datetime(df_gisaid['Collection_date'], errors='coerce')
            dt_start_mask: pd.Series = (collection_datetimes >= dt_start)
            mask = mask & dt_start_mask
            logging.info(f'{mask.sum()} GISAID sequences filtered starting {dt_start}. {dt_start_mask.sum()}')
        else:
            logging.info(f'Could not parse datetime from "{date_start}". No date filtering applied.')

    if date_end:
        dt_end: pd.Timestamp = pd.to_datetime(date_end, errors='coerce')
        if not pd.isna(dt_end):
            collection_datetimes: pd.Series = pd.to_datetime(df_gisaid['Collection_date'], errors='coerce')
            dt_end_mask: pd.Series = (collection_datetimes <= dt_end)
            mask = mask & dt_end_mask
            logging.info(f'{mask.sum()} GISAID sequences filtered ending {dt_end}.')
        else:
            logging.info(f'Could not parse datetime from "{date_start}". No date filtering applied.')

    if country:
        if ',' in country:
            countries = [x.strip() for x in country.split(',') if x.strip() != '']
            mask = mask & df_gisaid['country'].isin(countries)
            logging.info(f'{mask.sum()} GISAID sequences after filtering for countries: {countries}')
        else:
            mask = mask & df_gisaid['country'].str.contains(country)
            logging.info(f'{mask.sum()} GISAID sequences after filtering for country "{country}"')
    if region:
        if ',' in region:
            regions = [x.strip() for x in region.split(',') if x.strip() != '']
            mask = mask & df_gisaid['region'].isin(regions)
            logging.info(f'{mask.sum()} GISAID sequences after filtering for regions: "{regions}"')
        else:
            mask = mask & df_gisaid['region'].str.contains(region)
            logging.info(f'{mask.sum()} GISAID sequences after filtering for region "{region}"')
    df_subset: pd.DataFrame = df_gisaid.loc[mask, :]
    # drop duplicate entries of df_subset before filtering/sampling
    df_subset = df_subset[~df_subset.index.duplicated()]  # default keep first occurrence
    logging.info(f'{df_subset.shape[0]} interest strains found ')
    if df_subset.index.size > max_gisaid_seqs:
        logging.warning(f'There are {df_subset.index.size} GISAID sequences selected by metadata. '
                        f'Down-sampling to {max_gisaid_seqs}')
        sampled_gisaid = sampling_gisaid(df_subset, max_gisaid_seqs)
        df_subset = df_subset.loc[sampled_gisaid, :]
    metadata_filtered_sequences = set(df_subset.index)
    if not metadata_filtered_sequences:
        logging.error(f'No GISAID sequences found matching filters!')
        sys.exit(1)
    logging.info(f'Writing output FASTA with up to {len(metadata_filtered_sequences)} metadata filtered sequences to '
                 f'"{fasta_output}". Performing additional filtering for sequences with up to {max_ambig} ambiguous '
                 f'bases and length between {min_length} and {max_length}.')
    keep_samples: Set[str] = write_fasta(
        fasta_output,
        gisaid_fasta,
        max_ambig,
        max_length,
        metadata_filtered_sequences,
        min_length,
        user_fasta
    )
    logging.info(f'Wrote {len(keep_samples)} sequences to "{fasta_output}"')
    logging.info(f'Writing filtered metadata table with {keep_samples} entries to "{filtered_metadata}"')
    df_filtered = write_filtered_metadata(df_subset, filtered_metadata, keep_samples)
    logging.info(f'Writing Nextstrain metadata table to "{nextstrain_metadata}"')
    write_nextstrain_metadata(df_filtered, nextstrain_metadata)
    if statistics_output:
        lineage_counts = get_lineage_counts(gisaid_lineages, mask)
        stats = write_stats(
            output_path=statistics_output,
            gisaid_matching_lineage_counts=lineage_counts,
            n_total_gisaid_sequences=df_gisaid.shape[0],
            n_total_gisaid_lineages=gisaid_lineages.unique().size,
            n_gisaid_matching_lineage=n_gisaid_matching_lineage,
            n_metadata_filtered_sequences=df_subset.shape[0],
            n_final_filtered_sequences=df_filtered.shape[0],
            sample_lineages=sample_lineages
        )
        logging.info(f'Wrote GISAID filtering stats to "{statistics_output}"')
        logging.info(f'Filtering stats: {stats}')
    logging.info('Done!')


def get_lineage_counts(gisaid_lineages: pd.Series, mask: pd.Series) -> Dict[str, int]:
    return gisaid_lineages[mask].value_counts().to_dict()


def parse_fasta(gisaid_sequences: Path):
    with open(gisaid_sequences) as fin:
        yield SimpleFastaParser(fin)


def write_filtered_metadata(
        df_subset: pd.DataFrame,
        filtered_metadata: Path,
        keep_samples: Set[str]
) -> pd.DataFrame:
    df_filtered = df_subset.loc[keep_samples, :]
    df_filtered.to_csv(filtered_metadata, sep='\t', index=True)
    return df_filtered


def write_stats(
        output_path: Path,
        gisaid_matching_lineage_counts: Dict[str, int],
        n_total_gisaid_sequences: int,
        n_gisaid_matching_lineage: int,
        n_total_gisaid_lineages: int,
        n_metadata_filtered_sequences: int,
        n_final_filtered_sequences: int,
        sample_lineages: Set[str]
) -> Dict[str, Any]:
    import json
    stats = dict(
        sample_lineages=list(sample_lineages),
        n_total_gisaid_sequences=n_total_gisaid_sequences,
        n_total_gisaid_lineages=n_total_gisaid_lineages,
        n_gisaid_matching_lineage=n_gisaid_matching_lineage,
        gisaid_matching_lineage_counts=gisaid_matching_lineage_counts,
        n_metadata_filtered_sequences=n_metadata_filtered_sequences,
        n_final_filtered_sequences=n_final_filtered_sequences
    )
    with open(output_path, 'w') as fh:
        json.dump(stats, fh)
    return stats


def write_fasta(fasta_output, gisaid_sequences, max_ambig, max_length, metadata_filtered_sequences, min_length,
                sequences):
    with open(fasta_output, 'w') as fout:
        n_user_sequences = write_user_sequences(fout, sequences)
        logging.info(f'Wrote {n_user_sequences} user sequences to "{fasta_output}"')
        is_tarred = tarfile.is_tarfile(gisaid_sequences)
        logging.info(f'GISAID sequences from "{gisaid_sequences}" provided as {"TAR" if is_tarred else "FASTA"} file')
        iterator = read_fasta_tarxz(gisaid_sequences) if is_tarred else parse_fasta(gisaid_sequences)
        keep_samples = write_filtered_gisaid_seqs(fout, iterator, metadata_filtered_sequences, min_length, max_length,
                                                  max_ambig)
    return keep_samples


def init_logging():
    from rich.traceback import install
    console = Console(stderr=True, width=200)
    install(show_locals=True, width=200, word_wrap=True, console=console)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True,
                              tracebacks_show_locals=True,
                              locals_max_string=None,
                              console=console)],
    )


def sampling_gisaid(df: pd.DataFrame, max_gisaid_seqs: int) -> Set[str]:
    df_lineages_count = df['Pango_lineage'].value_counts(ascending=True).to_frame('count')
    n_lineages = df_lineages_count.shape[0]
    sampled_gisaid = set()
    seqs_per_lineages = int((max_gisaid_seqs - len(sampled_gisaid)) / n_lineages)
    for i, (lineage, row) in enumerate(df_lineages_count.iterrows()):
        seqs_in_lineages = df[df['Pango_lineage'] == lineage]
        if row['count'] < seqs_per_lineages:
            logging.info(
                f'No need to sample lineage "{lineage}" (sequences '
                f'count={row["count"]}; less than {seqs_per_lineages} seqs '
                f'per lineage)')
            sampled_gisaid |= set(seqs_in_lineages.index)
        else:
            try:
                weights = 1.0 - seqs_in_lineages['N_Content'].values
                weights[np.isnan(weights)] = 0.0
                weights = np.clip(weights, 0.0, 1.0)
                logging.info(
                    f'Using GISAID provided N content for down-sampling '
                    f'weights for {lineage}, (sequences count={row["count"]}; '
                    f'greater than {seqs_per_lineages} seqs per lineage)'
                    f'. Mean N content: {seqs_in_lineages["N_Content"].mean()}')
                sampled_gisaid |= set(seqs_in_lineages.index.to_series().sample(n=seqs_per_lineages, weights=weights))
            except ValueError as ex:
                logging.warning(
                    f'Could not use weights based on "N_Content" GISAID '
                    f'metadata field, using equal probability weights for '
                    f'down-sampling {lineage} (sequences count={row["count"]};'
                    f' greater than {seqs_per_lineages} seqs per lineage). '
                    f'Error: "{ex}"')
                sampled_gisaid |= set(seqs_in_lineages.index.to_series().sample(n=seqs_per_lineages))
        if n_lineages < i + 1:
            seqs_per_lineages = (max_gisaid_seqs - len(sampled_gisaid)) / (n_lineages - i + 1)
    return sampled_gisaid


def write_user_sequences(fout: IO[str], sequences: Path) -> int:
    count = 0
    with open(sequences) as fh:
        for name, seq in SimpleFastaParser(fh):
            fout.write(f'>{name}\n{seq}\n')
            count += 1
    return count


def write_nextstrain_metadata(df_filtered: pd.DataFrame, nextstrain_metadata: Path) -> None:
    """Save to metadata for nextstrain analysis, drop unnecessary columns"""
    drop_columns = ["Location",
                    "Additional_location_information",
                    "Sequence_length",
                    "Host",
                    "Patient_age",
                    "Gender",
                    "Clade",
                    "Pango_lineage",
                    "Pangolin_version",
                    "Variant",
                    "AA_Substitutions",
                    "Submission_date",
                    "Is_reference",
                    "Is_complete",
                    "Is_high_coverage",
                    "Is_low_coverage",
                    "N_Content",
                    "GC_Content"]
    df_subset_filtered = df_filtered.drop(columns=list(set(drop_columns) & set(df_filtered.columns)))
    # Need to specify exposure location as we specify country
    # The information missed in metadata so set them as the same as location information
    df_subset_filtered['region_exposure'] = df_subset_filtered['region']
    df_subset_filtered['country_exposure'] = df_subset_filtered['country']
    df_subset_filtered['division_exposure'] = df_subset_filtered['division']
    df_subset_filtered.to_csv(nextstrain_metadata, sep='\t', index=True)


def write_filtered_gisaid_seqs(
        handle: IO[str],
        header_seqs: Iterator[Tuple[str, str]],
        seq_ids: Set[str],
        min_length: int = 28000,
        max_length: int = 31000,
        n_ambiguous: int = 3000
) -> Set[str]:
    """Write GISAID sequences passing filters to FASTA file
    
    Filters include 
    - GISAID sequence IDs that were filtered from metadata table based on Pangolin lineage and other metadata
    - minimum length threshold
    - maximum length threshold
    - maximum number of ambiguous bases including N allowed in sequences
    
    Arguments:
        handle: Output file handle
        header_seqs: Iterator yielding tuple of header and sequence
        seq_ids: GISAID sequence IDs to output
        min_length: Minimum length of sequences
        max_length: Maximum length of sequences
        n_ambiguous: Max number of ambiguous bases in sequences

    Returns:
        Set of GISAID sequence names that were output
    """
    keep_samples = set()
    for strains, seq in header_seqs:
        if '|' in strains:
            strains = strains.split('|')[0]
        if ' ' in strains:
            strains = strains.replace(' ', '_')
        if strains not in seq_ids:
            continue
        if (
                min_length < len(seq) <= max_length
                and count_ambig_nt(seq) < n_ambiguous
                and strains not in keep_samples
        ):
            keep_samples.add(strains)
            handle.write(f'>{strains}\n{seq}\n')
    return keep_samples


def read_gisaid_metadata(gisaid_metadata: Path) -> pd.DataFrame:
    if tarfile.is_tarfile(gisaid_metadata):
        with tarfile.open(gisaid_metadata, "r:*") as tar:
            df = pd.read_table(get_file_from_tar(tar, r'.*\.tsv'), index_col=0)
    else:
        df = pd.read_table(gisaid_metadata, index_col=0)
    logging.info(f'Columns in GISAID metadata file: {df.columns}')
    # Replace non-word characters in column names with '_'
    df.columns = df.columns.str.replace(r'[^\w]+', '_', regex=True).str.replace(r'_+$', '', regex=True)
    # Strip whitespace from strain name
    df.index = df.index.str.replace(r'\s+', '_', regex=True)
    # Extract details of location into separate column
    df_locations = df['Location'].str.split(r'\s*/\s*', n=3, expand=True)
    df_locations.columns = ['region', 'country', 'division', 'city']
    return pd.concat([df, df_locations], axis=1)


def count_ambig_nt(seq: str) -> int:
    return sum(1 for x in seq.lower() if x not in {'a', 'g', 'c', 't', '-'})


def read_fasta_tarxz(tarxz_path) -> Iterator[Tuple[str, str]]:
    """Read first fasta file in a tar file"""
    # Skip any text before the first record (e.g. blank lines, comments)
    with tarfile.open(tarxz_path) as tar:
        handle = get_file_from_tar(tar, r'.*\.fasta$')
        for line in handle:
            line = line.decode()
            if line[0] == ">":
                title = line[1:].rstrip()
                break
            else:
                # no break encountered - probably an empty file
                return
        lines = []
        for line in handle:
            line = line.decode()
            if line[0] == ">":
                yield title, "".join(lines).replace(" ", "").replace("\r", "")
                lines = []
                title = line[1:].rstrip()
                continue
            lines.append(line.rstrip())
        yield title, "".join(lines).replace(" ", "").replace("\r", "")


def get_file_from_tar(tar: tarfile.TarFile, name: str) -> Optional[IO[bytes]]:
    while True:
        file_member = tar.next()
        if file_member is None:
            break
        if re.match(name, file_member.name):
            return tar.extractfile(file_member)


if __name__ == '__main__':
    typer.run(main)
