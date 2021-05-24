#!/usr/bin/env python3
import logging
import click
import pandas as pd
from ete3 import Tree


def count_taxa(newick_tree):
    count = 0
    for node in newick_tree.iter_leaf_names():
        count = count + 1
    return count

@click.command(context_settings = dict(help_option_names = ['-h', '--help']))
@click.option("-i", "--newick_tree_input", type = click.Path(exists = True), required = False, default ='')
@click.option("-M", "--metadata_input", type = click.Path(exists = True), required = False)
@click.option("-m", "--metadata_output", type = click.Path(exists = True), required = False)
@click.option("-R", "--ref_name", help="Name of reference sequence", required=False, type=str, default='MN908947.3')
@click.option("-r", "--lineage_report", help="Pangolin report of input sequences", type=click.Path(exists=False),
              required=False, default='')
@click.option("-max", "--max_taxa", required = False, type = int, default = 100)
@click.option("-min", "--min_taxa", required = False, type = int, default = 50)
@click.option("-l", "--leaflist", help="Leaves list", type=click.Path(exists=False),required=False)
def main(newick_tree_input, metadata_input, metadata_output , leaflist, ref_name, lineage_report, max_taxa, min_taxa):
    #read the tree
    phylo_tree = Tree(newick_tree_input)
    #read metadata

    df_metadata_input  = pd.read_table(metadata_input, sep='\t')
    df_metadata_output = pd.DataFrame(columns=df_metadata_input.columns)
    
    df_lineage_report = pd.read_table(lineage_report, sep=',')
    interest_list = df_lineage_report['taxon'].tolist()

    leaf_list = []
    for node in phylo_tree.iter_leaf_names():
        leaf_list.append(node)

    sub_tree_list  = []
    no_leaves_list = []

    for taxa in leaf_list:
        if taxa != ref_name:
            set_leaves = []
            for taxa_name in interest_list:
                set_leaves.append(taxa_name)
            set_leaves.append(taxa)
            ancestor = phylo_tree.get_common_ancestor(set_leaves)
            if count_taxa(ancestor) <= max_taxa:
                if '/' in taxa:
                    name = taxa.replace("/","_")
                sub_tree_list.append(ancestor)
                no_leaves_list.append(count_taxa(ancestor))
                #Write and plot tree for debugging
                ancestor.render(name + '.png', w=183, units="mm")
                ancestor.write(format=1, outfile= name+'.nw')

    if len(no_leaves_list) > 0:
        max_no_leaves = no_leaves_list.index(max(no_leaves_list))
        with open(leaflist, 'w') as fout:
            fout.write(ref_name+'\n')
            for x in sub_tree_list[max_no_leaves].iter_leaf_names():
                row_index = df_metadata_input.loc[df_metadata_input['strain'] == x].index
                df_metadata_output = df_metadata_output.append(df_metadata_input.loc[row_index])
                fout.write(f'{x}\n')
        df_metadata_output = df_metadata_output.drop(columns=[
                                                  "pangolin version",
                                                  "variant",
                                                  "AA Substitutions",
                                                  "Submission date",
                                                  "Is reference?",
                                                  "Is complete?",
                                                  "Is high coverage?",
                                                  "Is low coverage?",
                                                  "N-Content",
                                                  "GC-Content"])
        df_metadata_output.to_csv('metadata_output.tsv', sep='\t', index=False)
if __name__ == '__main__':
    main()
