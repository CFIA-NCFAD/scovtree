#!/usr/bin/env python3
import logging
import click
import pandas as pd


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-M", "--metadata-input", type=click.Path(exists=False), required=False, default='')
@click.option("-m", "--metadata-output", type=click.Path(exists=False), required=False, default='')
@click.option("-vn", "--skip-virus-name", type=bool, default=False, required=False)
@click.option("-t", "--skip-type", type=bool, default=False, required=False)
@click.option("-a", "--skip-accession-id", type=bool, default=False, required=False)
@click.option("-c", "--skip-collection-date", type=bool, default=False, required=False)
@click.option("-l", "--skip-location", type=bool, default=False, required=False)
@click.option("-al", "--skip-additional-location-information", type=bool, default=False, required=False)
@click.option("-s", "--skip-sequence-length", type=bool, default=False, required=False)
@click.option("-h", "--skip-host", type=bool, default=False, required=False)
@click.option("-p", "--skip-patient-age", type=bool, default=False, required=False)
@click.option("-g", "--skip-gender", type=bool, default=False, required=False)
@click.option("-c", "--skip-clade", type=bool, default=False, required=False)
@click.option("-pl", "--skip-pango-lineage", type=bool, default=False, required=False)
@click.option("-pv", "--skip-pangolin-version", type=bool, default=False, required=False)
@click.option("-va", "--skip-variant", type=bool, default=False, required=False)
@click.option("-aa", "--skip-aa-substitutions", type=bool, default=False, required=False)
@click.option("-sd", "--skip-submission-date", type=bool, default=False, required=False)
@click.option("-ir", "--skip-is-reference", type=bool, default=False, required=False)
@click.option("-ic", "--skip-is-complete", type=bool, default=False, required=False)
@click.option("-ih", "--skip-is-high-coverage", type=bool, default=False, required=False)
@click.option("-il", "--skip-is-low-coverage", type=bool, default=False, required=False)
@click.option("-n", "--skip-n-content", type=bool, default=False, required=False)
@click.option("-gc", "--skip-gc-content", type=bool, default=False, required=False)
def main(metadata_input, metadata_output, skip_virus_name, skip_type, skip_accession_id, skip_collection_date,
         skip_location,
         skip_additional_location_information, skip_sequence_length, skip_host, skip_patient_age, skip_gender,
         skip_clade, skip_pango_lineage, skip_pangolin_version, skip_variant, skip_aa_substitutions,
         skip_submission_date,
         skip_is_reference, skip_is_complete, skip_is_high_coverage, skip_is_low_coverage,
         skip_n_content, skip_gc_content):
    '''
    ['Virus_name', 'Type', 'Accession_ID', 'Collection_date', 'Location',
       'Additional_location_information', 'Sequence_length', 'Host',
       'Patient_age', 'Gender', 'Clade', 'Pango_lineage', 'Pangolin_version',
       'Variant', 'AA_Substitutions', 'Submission_date', 'Is_reference?',
       'Is_complete?', 'Is_high_coverage?', 'Is_low_coverage?', 'N-Content',
       'GC-Content']
    '''
    df_shiptv_metadata = pd.read_table(metadata_input, sep='\t')

    if skip_virus_name:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Virus_name"])
    if skip_type:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Type"])
    if skip_accession_id:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Accession_ID"])
    if skip_collection_date:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Collection_date"])
    if skip_location:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Location"])
    if skip_additional_location_information:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Additional_location_information"])
    if skip_sequence_length:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Sequence_length"])
    if skip_host:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Host"])
    if skip_patient_age:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Patient_age"])
    if skip_gender:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Gender"])
    if skip_clade:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Clade"])
    if skip_pango_lineage:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Pango_lineage"])
    if skip_pangolin_version:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Pangolin_version"])
    if skip_variant:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Variant"])
    if skip_aa_substitutions:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["AA_Substitutions"])
    if skip_submission_date:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Submission_date"])
    if skip_is_reference:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Is_reference?"])
    if skip_is_complete:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Is_complete?"])
    if skip_is_high_coverage:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Is_high_coverage?"])
    if skip_is_low_coverage:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["Is_low_coverage?"])
    if skip_n_content:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["N-Content"])
    if skip_gc_content:
        df_shiptv_metadata = df_shiptv_metadata.drop(columns=["GC-Content"])

    df_shiptv_metadata.to_csv(metadata_output, sep='\t', index=False)


if __name__ == '__main__':
    main()
