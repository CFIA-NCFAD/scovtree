#!/usr/bin/env python3
import logging
import click
import pandas as pd


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-M", "--metadata-input", type=click.Path(exists=False), required=False, default='')
@click.option("-m", "--metadata-output", type=click.Path(exists=False), required=False, default='')
@click.option("-ma", "--metadata-aa-change", type=click.Path(exists=False), required=False, default='')
@click.option("-p", "--pangolin-report", type=click.Path(exists=False), required=False, default='')
@click.option("-vg", "--visualize-gisiad-metadata", help="Specify columns in GISAID metadata for visualization",
              required=False, type=str, default='')
@click.option("-va", "--visualize-aa-change", help="Visualize aa substitution change", required=False, type=bool,
              default=True)
def main(metadata_input, metadata_output, metadata_aa_change, pangolin_report, visualize_gisiad_metadata,
         visualize_aa_change):

    gisaid_metadata_columns = ['Virus_name', 'Type', 'Accession_ID', 'Collection_date', 'Location',
                              'Additional_location_information', 'Sequence_length', 'Host',
                              'Patient_age', 'Gender', 'Clade', 'Pango_lineage', 'Pangolin_version',
                              'Variant', 'AA_Substitutions', 'Submission_date', 'Is_reference?',
                              'Is_complete?', 'Is_high_coverage?', 'Is_low_coverage?', 'N-Content',
                              'GC-Content']
    #Read gisaid metadata
    df_shiptv_metadata = pd.read_table(metadata_input, sep='\t')

    # Read aa subsitution matrix change
    df_aa_change = pd.read_table(metadata_aa_change)
    df_aa_change.rename(columns={"Unnamed: 0": "Virus_name"}, inplace=True)

    #Read pangolin report
    df_pangolin_report = pd.read_table(pangolin_report, sep=',')

    #Write pangolin lineage and version of input sequences to metadata
    for i, vname in enumerate(df_pangolin_report.iloc[:, 0].tolist()):
        df_row = pd.DataFrame(columns=df_shiptv_metadata.columns, index=[0])
        df_row['Virus_name'] = vname
        df_row['Pango_lineage'] = df_pangolin_report.loc[i]['lineage']
        df_row['Pangolin_version'] = df_pangolin_report.loc[i]['pangoLEARN_version']
        df_shiptv_metadata = df_shiptv_metadata.append(df_row)

    if visualize_gisiad_metadata != '': #visualize for specific columns
        visualized_columns = visualize_gisiad_metadata.split(',')
        drop_columns = [col for col in gisaid_metadata_columns if col not in visualized_columns]
        if visualize_aa_change:
            df_shiptv_metadata_output = pd.merge(df_shiptv_metadata, df_aa_change, on=['Virus_name'])
        else:
            df_shiptv_metadata_output = df_shiptv_metadata
        for col in drop_columns:
            if col == 'Virus_name':
                continue
            df_shiptv_metadata_output = df_shiptv_metadata_output.drop(columns=[col.strip()])
        df_shiptv_metadata_output.to_csv(metadata_output, sep='\t', index=False)
    else: #visualize all information
        if visualize_aa_change:
            df_shiptv_metadata_output = pd.merge(df_shiptv_metadata, df_aa_change, on=['Virus_name'])
            df_shiptv_metadata_output.to_csv(metadata_output, sep='\t', index=False)
        else:
            df_shiptv_metadata.to_csv(metadata_output, sep='\t', index=False)


if __name__ == '__main__':
    main()
