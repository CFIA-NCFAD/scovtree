#!/usr/bin/env python3
import logging
import click
import pandas as pd
from Bio import Phylo

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-i", "--newick-tree-input", type=click.Path(exists=True), required=False, default='')
@click.option("-M", "--metadata-input", type=click.Path(exists=True), required=False,default='')
@click.option("-m", "--metadata-output", type=click.Path(exists=False), required=False, default='')
@click.option("-R", "--ref-name", help="Name of reference sequence", required=False, type=str, default='MN908947.3')
@click.option("-r", "--lineage-report", help="Pangolin report of input sequences", type=click.Path(exists=False),
              required=False, default='')
@click.option("-max", "--max-taxa", required=False, type=int, default=100)
@click.option("-l", "--leaflist", help="Leaves list", type=click.Path(exists=False), required=False)
def main(newick_tree_input, metadata_input, metadata_output, ref_name, lineage_report, max_taxa, leaflist):

    # read metadata
    df_metadata_input = pd.read_table(metadata_input, sep='\t')
    if len(df_metadata_input) > 250:
        # read the tree
        tree = Phylo.read(newick_tree_input, 'newick')
        df_metadata_output = pd.DataFrame(columns=df_metadata_input.columns)

        df_lineage_report = pd.read_table(lineage_report, sep=',')
        interest_taxa = df_lineage_report['taxon'].tolist()[0]

        clade_ncfad = list(tree.find_elements(target=interest_taxa))[0]

        clade_neighbors = set()
        for i, c in enumerate(tree.get_path(clade_ncfad)[::-1]):
            n_terminals = c.count_terminals()
            if n_terminals <= max_taxa:
                for nc in c.get_terminals():
                    clade_neighbors.add(nc.name)
            else:
                break
        with open('leaflist', 'w') as fout:
            fout.write(ref_name+'\n')
            for x in clade_neighbors:
                row_index = df_metadata_input.loc[df_metadata_input['strain'] == x].index
                df_metadata_output = df_metadata_output.append(df_metadata_input.loc[row_index])
                fout.write(f'{x}\n')

        df_metadata_output = df_metadata_output.drop(columns=["region", "country", "division", "city"])
        df_metadata_output.to_csv(metadata_output, sep='\t', index=False)
    else:
        df_metadata_input = df_metadata_input.drop(columns=["region", "country", "division", "city"])
        df_metadata_input.to_csv(metadata_output, sep='\t', index=False)
        tree = Phylo.read(newick_tree_input, 'newick')
        with open(leaflist, 'w') as fout:
           for node in tree.get_terminals():
                fout.write(f'{node.name}\n')

if __name__ == '__main__':
    main()
