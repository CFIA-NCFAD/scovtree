#!/usr/bin/env python3
import click
import pandas as pd
from Bio import Phylo

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-i", "--newick-tree-input", type=click.Path(exists=True), required=False, default='')
@click.option("-m", "--metadata-output", type=click.Path(exists=False), required=False, default='')
@click.option("-ma", "--metadata-aa-change", type=click.Path(exists=False), required=False, default='')
@click.option("-r", "--lineage-report", help="Pangolin report of input sequences", type=click.Path(exists=False),
              required=False, default='')
@click.option("-l", "--leaflist", help="Leaves list", type=click.Path(exists=False), required=False)
def main(newick_tree_input, metadata_output, lineage_report, leaflist, metadata_aa_change):

    df_lineage_report = pd.read_table(lineage_report, sep=',')
    df_aa_change = pd.read_table(metadata_aa_change)
    df_aa_change.rename(columns={"Unnamed: 0": "taxon"}, inplace=True)
    df_shiptv_metadata_output = pd.merge(df_lineage_report, df_aa_change, on=['taxon'])
    df_shiptv_metadata_output.to_csv(metadata_output, sep='\t', index=False)

    tree = Phylo.read(newick_tree_input, 'newick')
    with open(leaflist, 'w') as fout:
       for node in tree.get_terminals():
            fout.write(f'{node.name}\n')

if __name__ == '__main__':
    main()
