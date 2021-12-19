#!/usr/bin/env python
from pathlib import Path

import pandas as pd
import typer
from Bio.SeqIO.FastaIO import SimpleFastaParser


def main(
        input_sequences: Path,
        metadata_input: Path,
        pangolin_report: Path,
        output_sequences: Path = typer.Option('sequences.nextclade.fasta'),
        ref_name: str = typer.Option('MN908947.3', help='Reference sequence name')
):
    df_metadata = pd.read_table(metadata_input, dtype=str)
    df_metadata.set_index(df_metadata.columns[0], inplace=True)
    df_pangolin = pd.read_csv(pangolin_report, dtype=str)
    df_pangolin.set_index(df_pangolin.columns[0], inplace=True)
    samples = set(df_metadata.index.astype(str))
    samples.add(ref_name)
    samples |= set(df_pangolin.index.astype(str))
    with open(input_sequences) as fin, open(output_sequences, 'w') as fout:
        for sample, seq in SimpleFastaParser(fin):
            if sample in samples:
                fout.write(f'>{sample}\n{seq}\n')


if __name__ == '__main__':
    typer.run(main)
