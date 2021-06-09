#!/usr/bin/env python3
import click
import pandas as pd
from Bio.SeqIO.FastaIO import SimpleFastaParser

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-i", "--input_sequences", type=click.Path(exists=True), required=False, default='')
@click.option("-m", "--metadata_input", type=click.Path(exists=True), required=False,default='')
@click.option("-o", "--output_sequences", type=click.Path(exists=False), required=False, default='')
def main(input_sequences, metadata_input, output_sequences):

    # read metadata
    df_metadata = pd.read_table(metadata_input, sep='\t')
    df = df_metadata.iloc[:,0]
    strain_list = df.tolist()

    sequences_dict= {}
    with open(input_sequences) as fin:
        for strains, seq in SimpleFastaParser(fin):
            sequences_dict[strains] = seq

    with open(output_sequences, 'w') as fout:
        for name in strain_list:
            fout.write(f'>{name}\n{sequences_dict[name]}\n')

if __name__ == '__main__':
    main()