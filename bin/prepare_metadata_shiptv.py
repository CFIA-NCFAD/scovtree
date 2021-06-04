#!/usr/bin/env python3
import click
import pandas as pd
from Bio import Phylo

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-i", "--newick_tree_input", type=click.Path(exists=True), required=False, default='')
@click.option("-m", "--metadata_output", type=click.Path(exists=False), required=False, default='')
@click.option("-r", "--lineage_report", help="Pangolin report of input sequences", type=click.Path(exists=False),
              required=False, default='')
@click.option("-l", "--leaflist", help="Leaves list", type=click.Path(exists=False), required=False)
def main(newick_tree_input, metadata_output, lineage_report, leaflist):

    df_lineage_report = pd.read_table(lineage_report, sep=',', index_col='taxon')
    df_lineage_report.to_csv(metadata_output, sep ='\t')
    tree = Phylo.read(newick_tree_input, 'newick')
    with open(leaflist, 'w') as fout:
       for node in tree.get_terminals():
            fout.write(f'{node.name}\n')

if __name__ == '__main__':
    main()
