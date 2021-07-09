#!/usr/bin/env python
import logging
import sys
import tarfile
from pathlib import Path
from typing import Iterator, Tuple, Optional, IO, Set
import re

import pandas as pd
import numpy as np
import typer
from Bio.SeqIO.FastaIO import SimpleFastaParser
from rich.logging import RichHandler


def main(
        sequences: Path,
        gisaid_sequences: Path,
        gisaid_metadata: Path,
        lineage_report: Path,
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
        fasta_output: Path = typer.Option(Path('gisaid_sequences.filtered.fasta'),
                                          help='Filtered GISAID sequences.'),
        filtered_metadata: Path = typer.Option(Path('gisaid_metadata.filtered.tsv'),
                                               help='Filtered GISAID metadata table.'),
        nextstrain_metadata: Path = typer.Option(Path('gisaid_metadata.nextstrain.tsv'),
                                                 help='Filtered GISAID metadata table for Nextstrain analysis.'),
        statistics_output: Path = typer.Option(Path('gisaid_stats.json'),
                                               help='GISAID filtering stats.')
):
    from rich.traceback import install
    install(show_locals=True, width=200, word_wrap=True)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True, locals_max_string=200)],
    )
    df_lineage_report = pd.read_csv(lineage_report, index_col=0)
    sample_lineages = set(df_lineage_report['lineage'])
    logging.info(f'{len(sample_lineages)} unique Pangolin lineages for user sequences: {sample_lineages}')
    df_gisaid = read_gisaid_metadata(gisaid_metadata)
    logging.info(
        f'Read GISAID metadata table from "{gisaid_metadata}"; {df_gisaid.shape[0]} rows and {df_gisaid.shape[1]} columns')

    gisaid_pango_lineage = df_gisaid['Pango_lineage']
    mask: pd.Series = gisaid_pango_lineage.isin(sample_lineages)
    n_gisaid_matching_lineage = mask.sum()
    logging.info(f'Found {n_gisaid_matching_lineage} GISAID sequences matching lineages {sample_lineages}.')
    if country:
        mask = mask & df_gisaid['country'].str.contains(country)
        logging.info(f'{mask.sum()} GISAID sequences after filtering for country "{country}"')
    if region:
        mask = mask & df_gisaid['region'].str.contains(region)
        logging.info(f'{mask.sum()} GISAID sequences after filtering for region "{region}"')
    df_subset: pd.DataFrame = df_gisaid.loc[mask, :]
    # drop duplicate entries of df_subset before filtering/sampling
    df_subset = df_subset[~df_subset.index.duplicated()]  # default keep first occurrence
    logging.info(f'{df_subset.shape[0]} interest strains found ')
    if df_subset.index.size > max_gisaid_seqs:
        logging.warning(f'There are {df_subset.index.size} GISAID sequences selected by metadata. '
                        f'Downsampling to {max_gisaid_seqs}')
        sampled_gisaid = sampling_gisaid(df_subset, max_gisaid_seqs)
        df_subset = df_subset.loc[sampled_gisaid, :]
    metadata_filtered_sequences = set(df_subset.index)
    if not metadata_filtered_sequences:
        logging.error(f'No GISAID sequences found matching filters!')
        sys.exit(1)

    with open(fasta_output, 'w') as fout:
        write_user_sequences(fasta_output, fout, sequences)
        if tarfile.is_tarfile(gisaid_sequences):
            logging.info(f'GISAID sequences provided as TAR file "{gisaid_sequences}"')
            iterator = read_fasta_tarxz(gisaid_sequences)
            keep_samples = write_good_seqs(
                iterator,
                metadata_filtered_sequences,
                fout,
                min_length,
                max_length,
                max_ambig
            )
        else:
            with open(gisaid_sequences) as fin:
                iterator = SimpleFastaParser(fin)
                keep_samples = write_good_seqs(
                    iterator,
                    metadata_filtered_sequences,
                    fout,
                    min_length,
                    max_length,
                    max_ambig
                )
    df_filtered = df_subset.loc[keep_samples, :]
    df_filtered.to_csv(filtered_metadata, sep='\t', index=True)

    write_nextstrain_metadata(df_filtered, nextstrain_metadata)

    if statistics_output:
        import json
        gisaid_matching_lineage_counts = gisaid_pango_lineage[gisaid_pango_lineage.isin(sample_lineages)] \
            .value_counts().to_dict()
        gisaid_matching_lineage_counts = {k: int(v) for k, v in gisaid_matching_lineage_counts.items()}
        stats = dict(
            sample_lineages=list(sample_lineages),
            n_total_gisaid_sequences=int(df_gisaid.shape[0]),
            n_total_gisaid_lineages=int(gisaid_pango_lineage.unique().size),
            n_gisaid_matching_lineage=int(n_gisaid_matching_lineage),
            gisaid_matching_lineage_counts=gisaid_matching_lineage_counts,
            n_metadata_filtered_sequences=int(df_subset.shape[0]),
            n_total_filtered_sequences=int(df_filtered.shape[0])
        )
        with open(statistics_output, 'w') as fh:
            json.dump(stats, fh)


def sampling_gisaid(df: pd.DataFrame, max_gisaid_seqs: int) -> Set[str]:
    df_lineages_count = df['Pango_lineage'].value_counts(ascending=True).to_frame('count')
    n_lineages = df_lineages_count.shape[0]
    sampled_gisaid = set()
    seqs_per_lineages = int((max_gisaid_seqs - len(sampled_gisaid)) / n_lineages)
    for i, (lineage, row) in enumerate(df_lineages_count.iterrows()):
        seqs_in_lineages = df[df['Pango_lineage'] == lineage]
        if row['count'] < seqs_per_lineages:
            logging.info(
                f'No need to sample lineage "{lineage}" (sequences count={row["count"]}; less than {seqs_per_lineages} seqs per lineage)')
            sampled_gisaid |= set(seqs_in_lineages.index)
        else:
            try:
                weights = 1.0 - seqs_in_lineages['N_Content'].values
                weights[np.isnan(weights)] = 0.0
                weights = np.clip(weights, 0.0, 1.0)
                logging.info(
                    f'Using GISAID provided N content for down-sampling weights for {lineage}, (sequences count={row["count"]}; greater than {seqs_per_lineages} seqs per lineage)'
                    f'. Mean N content: {seqs_in_lineages["N_Content"].mean()}')
                sampled_gisaid |= set(seqs_in_lineages.index.to_series().sample(n=seqs_per_lineages, weights=weights))
            except ValueError as ex:
                logging.warning(
                    f'Could not use weights based on "N_Content" GISAID metadata field, using equal probability weights for down-sampling {lineage}'
                    f'(sequences count={row["count"]}; greater than {seqs_per_lineages} seqs per lineage). Error: "{ex}"')
                sampled_gisaid |= set(seqs_in_lineages.index.to_series().sample(n=seqs_per_lineages))
        if n_lineages < i + 1:
            seqs_per_lineages = (max_gisaid_seqs - len(sampled_gisaid)) / (n_lineages - i + 1)
    return sampled_gisaid


def write_user_sequences(fasta_output: Path, fout: IO[str], sequences: Path) -> None:
    count = 0
    with open(sequences) as fh:
        for name, seq in SimpleFastaParser(fh):
            fout.write(f'>{name}\n{seq}\n')
            count += 1
    logging.info(f'Wrote {count} user sequences to "{fasta_output}"')


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


def write_good_seqs(
        header_seq_iterator: Iterator[Tuple[str, str]],
        metadata_filtered_sequences: Set[str],
        fasta_output_handle: IO[str],
        min_length: int = 28000,
        max_length: int = 31000,
        xambig: int = 3000
) -> Set[str]:
    keep_samples = set()
    for strains, seq in header_seq_iterator:
        if '|' in strains:
            strains = strains.split('|')[0]
        if ' ' in strains:
            strains = strains.replace(' ', '_')
        if strains not in metadata_filtered_sequences:
            continue
        if (
                min_length < len(seq) <= max_length
                and count_ambig_nt(seq) < xambig
                and strains not in keep_samples
        ):
            keep_samples.add(strains)
            fasta_output_handle.write(f'>{strains}\n{seq}\n')
    return keep_samples


def read_gisaid_metadata(gisaid_metadata: Path) -> pd.DataFrame:
    if tarfile.is_tarfile(gisaid_metadata):
        with tarfile.open(gisaid_metadata, "r:*") as tar:
            df = pd.read_table(get_file_from_tar(tar, r'.*\.tsv'), index_col=0)
    else:
        df = pd.read_table(gisaid_metadata, index_col=0)
    logging.info(f'Columns in GISAID metadata file: {df.columns}')
    # Replace non-word characters in column names with '_'
    df.columns = df.columns.str.replace(r'[^\w]+', '_').str.replace(r'_+$', '')
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
        file_member = tar.next()  # next() method is much faster than getnames() method
        if file_member is None:
            break
        if re.match(name, file_member.name):
            return tar.extractfile(file_member)


if __name__ == '__main__':
    typer.run(main)
