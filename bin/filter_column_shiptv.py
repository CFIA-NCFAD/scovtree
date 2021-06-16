#!/usr/bin/env python3
import logging
import click
import pandas as pd


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-M", "--metadata-input", type=click.Path(exists=False), required=False, default='')
@click.option("-m", "--metadata-output", type=click.Path(exists=False), required=False, default='')
@click.option("-ma", "--metadata-aa-change", type=click.Path(exists=False), required=False, default='')
@click.option("-p", "--pangolin-report", type=click.Path(exists=False), required=False,default='')
@click.option("-d", "--drop-gisiad-columns", help="Drop GISIAD Columns", required=False, type=str, default='')
def main(metadata_input, metadata_output, metadata_aa_change, pangolin_report, drop_gisiad_columns):

    '''
    ['Virus_name', 'Type', 'Accession_ID', 'Collection_date', 'Location',
       'Additional_location_information', 'Sequence_length', 'Host',
       'Patient_age', 'Gender', 'Clade', 'Pango_lineage', 'Pangolin_version',
       'Variant', 'AA_Substitutions', 'Submission_date', 'Is_reference?',
       'Is_complete?', 'Is_high_coverage?', 'Is_low_coverage?', 'N-Content',
       'GC-Content']
    Columns aa_substitution_change is used for aa change visualization
    '''

    df_shiptv_metadata = pd.read_table(metadata_input, sep='\t')

    df_aa_change = pd.read_table(metadata_aa_change)
    df_aa_change.rename(columns={"Unnamed: 0": "Virus_name"}, inplace=True)

    df_pangolin_report = pd.read_table(pangolin_report, sep=',')

    for i, vname in enumerate(df_pangolin_report.iloc[:,0].tolist()):
        df_row = pd.DataFrame(columns=df_shiptv_metadata.columns, index=[0])
        df_row['Virus_name'] = vname
        df_row['Pango_lineage'] = df_pangolin_report.loc[i]['lineage']
        df_row['Pangolin_version'] = df_pangolin_report.loc[i]['pangoLEARN_version']
        df_shiptv_metadata = df_shiptv_metadata.append(df_row)


    if (drop_gisiad_columns !=''):
        drop_columns = drop_gisiad_columns.split(',')
        if 'aa_substitution_change' not in drop_columns: # merge aa_change into shiptv_metadata
            df_shiptv_metadata_output = pd.merge(df_shiptv_metadata, df_aa_change, on=['Virus_name'])
        else: # otherwise keep it unchanged,
            df_shiptv_metadata_output = df_shiptv_metadata
        for col in drop_columns:
            if col != 'aa_substitution_change':
                df_shiptv_metadata_output = df_shiptv_metadata_output.drop(columns=[col.strip()])
        df_shiptv_metadata_output.to_csv(metadata_output, sep='\t', index=False)
    else:
        df_shiptv_metadata_output = pd.merge(df_shiptv_metadata, df_aa_change, on=['Virus_name'])
        df_shiptv_metadata_output.to_csv(metadata_output, sep='\t', index=False)

if __name__ == '__main__':
    main()
