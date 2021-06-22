#!/usr/bin/env python3
import logging
import sys
from pathlib import Path
from typing import Iterable, Set

import pandas as pd
import typer
from Bio import Phylo
from Bio.Phylo.Newick import Tree, Clade
from rich.logging import RichHandler


def main(
    newick_tree_input: Path,
    metadata_input: Path,
    lineage_report: Path = typer.Option(..., help="Pangolin lineage report CSV"),
    ref_name: str = typer.Option("MN908947.3", help="Reference/outgroup name"),
    leaflist: Path = typer.Option(Path('leaflist'), help='List of leaves/taxa to filter for in shiptv tree'),
    metadata_output: Path = typer.Option('metadata.leaflist.tsv', help='Metadata for leaflist taxa'),
    max_taxa: int = typer.Option(100, help="Max taxa in leaflist"),
):
    """Prune phylo tree to taxa neighboring user taxa"""
    from rich.traceback import install
    install(show_locals=True)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )
    df = pd.read_table(metadata_input, index_col=0)
    logging.info(f'Read metadata table "{metadata_input}" with {df.shape[0]} rows.')
    tree: Tree = Phylo.read(newick_tree_input, "newick")
    n_taxa = tree.count_terminals()
    logging.info(f'Read tree "{newick_tree_input}" with {n_taxa}.')
    if n_taxa <= max_taxa:
        logging.info(f'No pruning of tree required. Number of taxa ({n_taxa}) '
                     f'less than/equal to max taxa desired in tree ({max_taxa}). '
                     f'Writing leaflist "{leaflist}" with all {n_taxa} taxa.')
        write_leaflist((n.name for n in tree.get_terminals()), leaflist)
        logging.info(f'Symlinking "{metadata_output}" to "{metadata_input}".')
        metadata_output.symlink_to(metadata_input.resolve())
        sys.exit(0)

    df_lineage_report = pd.read_csv(lineage_report, index_col=0)
    clade_neighbors = {ref_name}
    user_taxa = set(df_lineage_report.index)
    # add user sequences to leaf list output
    clade_neighbors |= user_taxa
    clade_neighbors = get_neighbors(tree, user_taxa, clade_neighbors, max_taxa)
    write_leaflist(clade_neighbors, leaflist)
    df.loc[list(clade_neighbors), :].to_csv(metadata_output, sep="\t")


def get_neighbors(tree: Tree, user_taxa: Set[str], clade_neighbors: Set[str], max_taxa: int) -> Set[str]:
    # TODO: implement adding neighboring taxa equally for all user taxa based on branch distance [peterk87 2021-06-22]
    for user_taxon in user_taxa:
        user_taxon_node = list(tree.find_elements(target=user_taxon))[0]
        clade: Clade
        for clade in tree.get_path(user_taxon_node)[::-1]:
            n_terminals = clade.count_terminals()
            if n_terminals <= max_taxa:
                clade_neighbors |= {nc.name for nc in clade.get_terminals()}
            else:
                break
    return clade_neighbors


def write_leaflist(clade_neighbors: Iterable[str], leaflist: Path) -> None:
    with open(leaflist, "w") as fout:
        for x in clade_neighbors:
            fout.write(f"{x}\n")


if __name__ == "__main__":
    typer.run(main)
