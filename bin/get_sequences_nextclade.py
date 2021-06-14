#!/usr/bin/env python3
import click
import pandas as pd
from Bio.SeqIO.FastaIO import SimpleFastaParser

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-i", "--input-sequences", type=click.Path(exists=True), required=False, default='')
@click.option("-m", "--metadata-input", type=click.Path(exists=True), required=False,default='')
@click.option("-mp", "--pangolin-report", type=click.Path(exists=True), required=False,default='')
@click.option("-R", "--ref-name", help="Name of reference sequence", required=False, type=str, default='MN908947.3')
@click.option("-o", "--output-sequences", type=click.Path(exists=False), required=False, default='')
def main(input_sequences, metadata_input, pangolin_report, output_sequences, ref_name):

    # read metadata
    df_metadata = pd.read_table(metadata_input, sep='\t')
    df_pangolin_report = pd.read_table(pangolin_report, sep=',')
    df = df_metadata.iloc[:,0]
    strain_list = df.tolist()
    strain_list.append(ref_name)
    for vname in df_pangolin_report.iloc[:,0].tolist():
        strain_list.append(vname)

    sequences_dict={}
    with open(input_sequences) as fin:
        for strains, seq in SimpleFastaParser(fin):
            sequences_dict[strains] = seq

    with open(output_sequences, 'w') as fout:
        for name in strain_list:
            fout.write(f'>{name}\n{sequences_dict[name]}\n')

if __name__ == '__main__':
    main()
