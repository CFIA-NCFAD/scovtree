#!/usr/bin/env python3
import click
import pandas as pd
import numpy as np

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-m", "--metadata-input", type=click.Path(exists=True), required=False,default='')
@click.option("-o", "--metadata-output", type=click.Path(exists=False), required=False, default='')
def main(metadata_input, metadata_output):

    df_nextclade =pd.read_table(metadata_input, sep=';')
    aasubs = df_nextclade['aaSubstitutions'].str.replace('(^\(|\)$)', '', regex=True).str.split(',')

    sample_aas = {}
    for vname, aas in zip(df_nextclade['seqName'], aasubs):
        if not isinstance(aas, list):
            continue
        sample_aas[vname] = set(aas)

    # Get the list samples
    samples = (list(sample_aas))

    unique_aas = set()
    for aas in sample_aas.values():
        unique_aas |= aas
    unique_aas = list(unique_aas)
    unique_aas.sort()

    arr_aas = np.zeros((len(sample_aas), len(unique_aas)), dtype='uint8')
    # if AA sub present in sample, set index of sample, aa sub to 1
    for i, sample in enumerate(samples):
        df_sample = df_nextclade.loc[df_nextclade['seqName'] == sample]
        sample_aasubs = df_sample['aaSubstitutions'].str.replace('(^\(|\)$)', '', regex=True).str.split(',').tolist()[0]
        for aa in sample_aasubs:
            j = unique_aas.index(aa)
            arr_aas[i, j] = 1

    dfaa = pd.DataFrame(arr_aas, index=samples, columns=unique_aas)
    dfaa.to_csv(metadata_output, sep='\t')

if __name__ == '__main__':
    main()
