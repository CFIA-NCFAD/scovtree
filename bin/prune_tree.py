#!/usr/bin/env python3
import logging
import sys
from pathlib import Path
from typing import Iterable, Set, Dict, Tuple, List

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
    install(show_locals=True, width=120, word_wrap=True)
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
    logging.info(f'Read Pangolin lineage report with {df_lineage_report.index.size} rows.')
    user_taxa = set(df_lineage_report.index)
    logging.info(f'User taxa in tree determined to be {user_taxa}')
    logging.info(f'Getting neighboring nodes for user taxa up to {max_taxa} taxa in total.')
    clade_neighbors = get_neighbors(tree, user_taxa, max_taxa - 1)
    logging.info(f'Found {len(clade_neighbors - user_taxa)} neighboring taxa to {len(user_taxa)} '
                 f'user taxa. Writing leaf list.')
    clade_neighbors.add(ref_name)
    write_leaflist(clade_neighbors, leaflist)
    df.loc[list(clade_neighbors & set(df.index)), :].to_csv(metadata_output, sep="\t")


def get_clade_member_distances(
        tree: Tree,
        name_node: Dict[str, Clade],
        tax: str,
        max_taxa: int
) -> List[Tuple[float, str]]:
    user_node = name_node[tax]
    clade = user_node
    for clade in tree.get_path(user_node)[::-1]:
        if clade.count_terminals() > max_taxa:
            break
    return sorted((tree.distance(user_node, x), x.name) for x in clade.get_terminals() if x != user_node)


def get_neighbors(tree: Tree, user_taxa: Set[str], max_taxa: int) -> Set[str]:
    name_node = {x.name: x for x in tree.get_terminals()}
    logging.info(f'Calculating branch distances between {len(user_taxa)} user taxa and neighboring taxa.')
    user_tax_to_distances = {tax: get_clade_member_distances(tree, name_node, tax, max_taxa=max_taxa)
                             for tax in user_taxa}
    leaflist = set() | user_taxa
    n_terminals = tree.count_terminals()
    max_taxa = min(max_taxa, n_terminals)
    while len(leaflist) < max_taxa:
        for user_tax, dists in user_tax_to_distances.items():
            if not dists:
                continue
            dist, name = dists.pop(0)
            leaflist.add(name)
    return leaflist


def write_leaflist(clade_neighbors: Iterable[str], leaflist: Path) -> None:
    with open(leaflist, "w") as fout:
        for x in clade_neighbors:
            fout.write(f"{x}\n")


if __name__ == "__main__":
    typer.run(main)
