#!/usr/bin/env python3
import logging
import click
import pandas as pd
from Bio.SeqIO.FastaIO import SimpleFastaParser
from collections import Counter
import tarfile

def count_ambig_nt(seq: str) -> int:
    counter = Counter(seq.lower())
    return sum(v for k, v in counter.items() if k not in {'a', 'g', 'c', 't', '-'})

def format_date(sampling_date: str) -> str:
    if '-' not in sampling_date:  # contain year only
        return sampling_date + '-XX-XX'  # 2020-XX-XX
    else:
        sampling_date_list = sampling_date.split('-')
        if len(sampling_date_list) == 2:
            return sampling_date + '-XX'  # 2020-02-XX
        elif len(sampling_date_list) == 3:
            return sampling_date # 2020-02-01

def format_strain_name(strain: str) -> str:
    if ' ' in strain:
        strain = strain.replace(' ', '_')
        return strain
    else:
        return strain


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-lmin", "--lmin", help="ignore sequences w/length < lmin", required=False, type=int, default=20000)
@click.option("-lmax", "--lmax", help="ignore sequences w/length >= lmax", required=False, type=int, default=32000)
@click.option("-x", "--xambig", help="ignore sequences with >=  xambig ambiguous residues", required=False, type=int,
              default=3000)
@click.option("-i", "--gisaid_sequences", type=click.Path(exists=True), required=True)
@click.option("-m", "--gisiad_metadata", type=click.Path(exists=True), required=True)
@click.option("-R", "--lineage_report", type=click.Path(exists=True), required=False, default ='')
# @click.option("-ref", "--ref_sequence", type=click.Path(exists=True), required=False)
# @click.option("-seq", "--input_seq", type=click.Path(exists=True), required=False)
@click.option("-s", "--sample_lineage", type=str, required=True, default ='')
@click.option("-c", "--country", help="Country", required=False, type=str, default='')
@click.option("-r", "--region", help="Region", required=False, type=str, default='')
@click.option("-of", "--fasta_output", type=click.Path(exists=False), required=True)
@click.option("-om1", "--metadata_output1", help="New format of metadata", type=click.Path(exists=False), required=True)
@click.option("-om2", "--metadata_output2", help="Old format of metadata", type=click.Path(exists=False), required=True)
@click.option("-ot", "--statistics_output", help="Statistics output", type=click.Path(exists=False), required=True)
def main(lmin, lmax, xambig, gisaid_sequences, gisiad_metadata, lineage_report, sample_lineage, country, region, fasta_output,
         metadata_output1, metadata_output2, statistics_output):

    lineage = ''
    if lineage_report != '':
        df_lineage_report = pd.read_table(lineage_report, sep=',')
        df_lineage_report.drop_duplicates(subset=['lineage'], inplace=True)
        lineage = df_lineage_report['lineage'][0]
    else:
        lineage = sample_lineage

    # Rename gisiad metadata according below format, 22 columns in metadata file
    column_names = ["strain",
                    "virus",
                    "gisaid_epi_isl",
                    "date",
                    "location",
                    "Additional location information",
                    "length",
                    "host",
                    "age",
                    "sex",
                    "clade",
                    "pango lineage",
                    "pangolin version",
                    "variant",
                    "AA Substitutions",
                    "Submission date",
                    "Is reference?",
                    "Is complete?",
                    "Is high coverage?",
                    "Is low coverage?",
                    "N-Content",
                    "GC-Content"]
    # Parse gisiad metadata into dataframe
    if tarfile.is_tarfile(gisiad_metadata):
        with tarfile.open(gisiad_metadata, "r:*") as tar:
            csv_path = list(n for n in tar.getnames() if n.endswith('.tsv'))[0]
            df_gisiad = pd.read_table(tar.extractfile(csv_path))
    else:
        df_gisiad = pd.read_table(gisiad_metadata)
    # Rename columns according to column_names
    df_gisiad.columns = column_names

    # Reformat sampling date
    df_gisiad['date'] = df_gisiad['date'].apply(format_date)
    # Reformat strain name
    df_gisiad['strain'] = df_gisiad['strain'].apply(format_strain_name)

    # Extract details of location into separate column
    df_locations = df_gisiad['location'].str.split(r'\s*/\s*', n=3, expand=True)
    df_locations.columns = ['region', 'country', 'division', 'city']
    df_locations = df_locations.astype('category')
    # add extracted location info to output DF
    df_gisiad_metadata = pd.concat([df_gisiad, df_locations], axis=1)

    #df_gisiad_metadata.drop_duplicates(subset=['strain'], inplace=True)

    # Filter sequences
    if country != '' and region != '':
        df_subset = df_gisiad_metadata.loc[((df_gisiad_metadata['pango lineage'] == lineage) &
                                            df_gisiad_metadata['location'].str.contains(region) & df_gisiad_metadata[
                                                'location'].str.contains(country)), :]
    elif country == '' and region != '':
        df_subset = df_gisiad_metadata.loc[((df_gisiad_metadata['pango lineage'] == lineage) &
                                            df_gisiad_metadata['location'].str.contains(region)), :]
    elif country != '' and region == '':
        df_subset = df_gisiad_metadata.loc[((df_gisiad_metadata['pango lineage'] == lineage) &
                                            df_gisiad_metadata['location'].str.contains(country)), :]
    elif country == '' and region == '':
        df_subset = df_gisiad_metadata.loc[(df_gisiad_metadata['pango lineage'] == lineage), :]

    num_lineage_found = df_subset.shape[0]
    # Drop rows have duplicate strain names
    # df_subset.drop_duplicates(subset = ['strain'], inplace = True)
    strains_of_interest = set(df_subset['strain'])
    len_strains_of_interest = len(strains_of_interest)
    num_seqs_found = 0
    if len(strains_of_interest) > 0:
        added_strains = []
        df_filtered = pd.DataFrame(columns = column_names)
        with open(gisaid_sequences) as fin, open(fasta_output, 'w') as fout:
            for strains, seq in SimpleFastaParser(fin):
                if '|' in strains:
                    strains = strains.split('|')[0]
                if ' ' in strains:
                    strains = strains.replace(' ', '_')
                if strains not in strains_of_interest:
                    continue
                if (lmin < len(seq) <= lmax) and (count_ambig_nt(seq) < xambig) and (strains not in added_strains) :
                    num_seqs_found = num_seqs_found + 1
                    added_strains.append(strains)
                    # Get metadata information
                    row_index = df_subset.loc[df_subset['strain'] == strains].index
                    df_filtered = df_filtered.append(df_subset.loc[row_index])
                    # Write sequences
                    fout.write(f'>{strains}\n{seq}\n')
                #else:
                    #count_drop = count_drop + 1
                    #df_subset.drop(df_subset.loc[df_subset['strain'] == strains].index, inplace=True)

        # Keep the current format of metadata
        df_filtered.to_csv(metadata_output1, sep='\t', index=False)
        # Save to metadata for nextstrain analysis, drop unnecessary columns
        df_subset_filtered = df_filtered.drop(columns=["location",
                                                  "Additional location information",
                                                  "length",
                                                  "host",
                                                  "age",
                                                  "sex",
                                                  "clade",
                                                  "pango lineage",
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
        # Need to specify exposure location as we specify country
        # The information missed in metadata so set them as the same as location information
        df_subset_filtered['region_exposure'] = df_subset_filtered['region']
        df_subset_filtered['country_exposure'] = df_subset_filtered['country']
        df_subset_filtered['division_exposure'] = df_subset_filtered['division']
        df_subset_filtered.to_csv(metadata_output2, sep='\t', index=False)
    else:
        logging.basicConfig(format='%(message)s',
                            datefmt='[%Y-%m-%d %X]',
                            level=logging.WARNING)
        log = logging.getLogger("rich")
        log.warning("No Interest Strains Found!")

    with open(statistics_output, 'w') as stat:
        stat.write(f'No_Strains_Interest\tNo_Strains_Found(After Filtering)\tNo_Strains_Duplicated\n')
        stat.write(f'{num_lineage_found}\t{num_seqs_found}\t{num_lineage_found - len_strains_of_interest}\n')


if __name__ == '__main__':
    main()
