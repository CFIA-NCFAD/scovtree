#!/usr/bin/env python
import logging
from pathlib import Path

import pandas as pd
import typer
from Bio import Phylo
from rich.logging import RichHandler


def main(
        newick_tree_input: Path,
        lineage_report: Path,
        metadata_aa_change: Path,
        leaflist: Path,
        metadata_output: Path,
):
    from rich.traceback import install
    install(show_locals=True, width=120, word_wrap=True)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    df_lineage_report = pd.read_csv(lineage_report, index_col=0)
    df_aa_change = pd.read_table(metadata_aa_change, index_col=0)
    df_out = pd.concat([df_lineage_report, df_aa_change], axis=1)
    df_out.to_csv(metadata_output, sep='\t', index=True)

    tree = Phylo.read(newick_tree_input, 'newick')
    with open(leaflist, 'w') as fout:
        for node in tree.get_terminals():
            fout.write(f'{node.name}\n')


if __name__ == '__main__':
    typer.run(main)
