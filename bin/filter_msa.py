#!/usr/bin/env python3
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Tuple, Mapping, Optional

import pandas as pd
import typer
from Bio.SeqIO.FastaIO import SimpleFastaParser
from rich.logging import RichHandler


def main(input_fasta: Path = typer.Option(..., help='FASTA with sequences to filter'),
         input_metadata: Path = typer.Option(..., help='Metadata for input sequences'),
         lineage_report: Path = typer.Option(..., help='Pangolin lineage report'),
         ref_name: str = typer.Option('MN908947.3'),
         country: Optional[str] = typer.Option(None, help='Preferentially filter for samples from this country'),
         max_seqs: int = typer.Option(10000, help='Max number of sequences to filter down to'),
         output_fasta: Path = typer.Option(Path('filtered.fasta'), help='Output filtered sequences FASTA'),
         output_metadata: Path = typer.Option(Path('metadata.filtered.tsv'), help='Output filtered metadata table')):
    """Filter MSA FASTA for user specified and higher quality public sequences up to `max_seqs`"""
    from rich.traceback import install
    install(show_locals=True, width=120, word_wrap=True)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    logging.info(f'Reading metadata table "{input_metadata}".')
    df = pd.read_table(input_metadata, index_col=0)
    nrow = df.shape[0]
    if nrow <= max_seqs:
        logging.info(f'MSA sequences ({nrow}) <= {max_seqs}. Creating symlinks...')
        make_symlinks(input_fasta, output_fasta, input_metadata, output_metadata)
        logging.info(f'Done!')
        sys.exit(0)
    logging.info(f'Filtering. {nrow} > {max_seqs} sequences.')
    sample_seq = read_fasta(input_fasta)
    seq_samples = seq_to_samples(sample_seq)
    keep_samples = init_samples_to_keep(lineage_report, ref_name)
    if country and 'country' in df.columns:
        keep_samples = keep_seqs_from_country(df, country, keep_samples, max_seqs)
    elif country:
        logging.warning(f'Country "{country}" to preferentially select sequences from '
                        f'specified, but no column "country" in metadata dataframe!')
    df_less_n_gaps, keep_samples = quality_filter(keep_samples, seq_samples, df)
    if (df_less_n_gaps.shape[0] + len(keep_samples)) <= max_seqs:
        keep_samples |= set(df_less_n_gaps['sample'])
    else:
        keep_samples = sampling_lineages(df_less_n_gaps, keep_samples, max_seqs)
        logging.info(f'Sampled {(len(keep_samples))} samples from top quality sequences.')
    logging.info(f'Writing {len(keep_samples)} of {len(seq_samples)} sequences to "{output_fasta}".')
    write_fasta(output_fasta, keep_samples, sample_seq)
    df.loc[keep_samples & set(df.index), :].to_csv(output_metadata, sep='\t', index=True)
    logging.info(f'Done!')


def sampling_lineages(df: pd.DataFrame, keep_samples: Set[str], max_seqs: int) -> Set[str]:
    df_lineages_count = df['lineage'].value_counts(ascending=True).to_frame('count')
    n_lineages = df_lineages_count.shape[0]
    seqs_per_lineages = int((max_seqs - len(keep_samples)) / n_lineages)
    for i, (lineage, row) in enumerate(df_lineages_count.iterrows()):
        seqs_in_lineages = df[df['lineage'] == lineage]
        if row['count'] < seqs_per_lineages:
            keep_samples |= set(seqs_in_lineages['sample'])
        else:
            keep_samples |= set(seqs_in_lineages['sample'].sample(n=seqs_per_lineages))
        if n_lineages < i + 1:
            seqs_per_lineages = (max_seqs - len(keep_samples)) / (n_lineages - i + 1)
    return keep_samples


def keep_seqs_from_country(df: pd.DataFrame, country: str, keep_samples: Set[str], max_seqs: int) -> Set[str]:
    country_matching_samples = set(df[df.country.str.contains(country, case=False)].index)
    n_country_keep = len(country_matching_samples | keep_samples)
    if n_country_keep <= max_seqs:
        logging.info(f'Keeping {n_country_keep} sequences matching country "{country}".')
        keep_samples |= country_matching_samples
    else:
        logging.info(f'{len(country_matching_samples)} country "{country}" samples '
                     f'and {len(keep_samples)} user sequences greater than '
                     f'{max_seqs} threshold. Randomly sampling all '
                     f'sequences based on quality.')
    return keep_samples


def quality_filter(keep_samples: Set[str], seq_samples: Mapping[str, Set[str]], df: pd.DataFrame) -> Tuple[pd.DataFrame, Set[str]]:
    seq_recs = []
    for seq, samples in seq_samples.items():
        if samples & keep_samples:
            keep_samples |= samples
            continue
        seq = seq.upper()
        # There are possible duplicate strains, add lineage column for df_less_n_gaps dataframe
        sample_lineage = set(df[df.index == list(samples)[0]]['Pango_lineage'])
        seq_recs.append(dict(
            sample=list(samples)[0],
            lineage=list(sample_lineage)[0],
            seq_n=seq.count('N'),
            seq_gap=seq.count('-'),
        ))
    df_seq_recs = pd.DataFrame(seq_recs)
    # TODO: more flexible and dynamic sequence quality filtering based on total number of sequences and number of sequences required so that sequences aren't unnecessarily filtered out [peterk87 2021-06-22]
    df_percentile_75 = df_seq_recs.describe()
    seq_n_75 = df_percentile_75.loc['75%', 'seq_n']
    seq_gap_75 = df_percentile_75.loc['75%', 'seq_gap']
    df_less_n_gaps = df_seq_recs.query('seq_n <= @seq_n_75 and seq_gap <= @seq_gap_75')
    return df_less_n_gaps, keep_samples


def write_fasta(fasta_output: Path, keep_samples: Set[str], sample_seq: Dict[str, str]) -> None:
    with open(fasta_output, 'w') as fout:
        for sample in keep_samples:
            fout.write(f'>{sample}\n{sample_seq[sample]}\n')


def init_samples_to_keep(lineage_report: Path, ref_name: str) -> Set[str]:
    df_lineage_report = pd.read_csv(lineage_report, index_col=0)
    keep_samples = set(df_lineage_report.index)
    keep_samples.add(ref_name)
    return keep_samples


def make_symlinks(input_fasta: Path,
                  fasta_output: Path,
                  metadata_input: Path,
                  metadata_output: Path):
    metadata_output.symlink_to(metadata_input.resolve())
    logging.info(f'Created symlink "{metadata_output}" to "{metadata_input}"')
    fasta_output.symlink_to(Path(input_fasta).resolve())
    logging.info(f'Created symlink "{fasta_output}" to "{input_fasta}"')


def read_fasta(fasta: Path) -> Dict[str, str]:
    out = {}
    with open(fasta) as fin:
        for strain, seq in SimpleFastaParser(fin):
            out[strain] = seq
    return out


def seq_to_samples(sample_seq: Dict[str, str]) -> Mapping[str, Set[str]]:
    seq_samples = defaultdict(set)
    for sample, seq in sample_seq.items():
        seq_samples[seq].add(sample)
    return seq_samples


if __name__ == '__main__':
    typer.run(main)
