#!/usr/bin/env python3
import logging
from pathlib import Path
import re
import gzip

import typer
from Bio.SeqIO.FastaIO import SimpleFastaParser
from rich.logging import RichHandler


def main(
    sequences: Path,
    fasta_output: Path = typer.Option(Path('input_sequences.correctedID.fasta'),
                                          help='FASTA Sequences with correct ID for Pangolin Analysis.'),
):
    from rich.traceback import install
    install(show_locals=True, width=200, word_wrap=True)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True, locals_max_string=200)],
    )
    with open(fasta_output, 'w') as fout:
        if '.gz' in Path(sequences).suffixes:
            logging.info(f'Input Sequences {sequences} in gz format provided')
            with gzip.open(sequences, 'rt') as fin:
                for name, seq in SimpleFastaParser(fin):
                    header = re.sub(r'[\|\s].*$', "", name)
                    fout.write(f'>{header}\n{seq}\n')
        else:
            logging.info(f'Input Sequences {sequences} in unzip format provided')
            with open(sequences, 'rt') as fin:
                for name, seq in SimpleFastaParser(fin):
                    header = re.sub(r'[\|\s].*$', "", name)
                    fout.write(f'>{header}\n{seq}\n')


if __name__ == "__main__":
    typer.run(main)
