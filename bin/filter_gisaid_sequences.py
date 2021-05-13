#!/usr/bin/env python3
import logging
from rich.logging import RichHandler
import click
import pandas as pd
from Bio.SeqIO.FastaIO import SimpleFastaParser
from collections import Counter


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


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-lmin", "--lmin", help="ignore sequences w/length < lmin", required=False, type=int, default=27000)
@click.option("-lmax", "--lmax", help="ignore sequences w/length >= lmax", required=False, type=int, default=32000)
@click.option("-x", "--xambig", help="ignore sequences with >=  xambig ambiguous residues", required=False, type=int,
              default=3000)
@click.option("-i", "--gisaid_sequences", type=click.Path(exists=True), required=True)
@click.option("-m", "--gisiad_metadata", type=click.Path(exists=True), required=True)
@click.option("-s", "--sample_lineage", type=str, required=True)
@click.option("-c", "--country", help="Country", required=False, type=str, default='')
@click.option("-r", "--region", help="Region", required=False, type=str, default='')
@click.option("-of", "--fasta_output", type=click.Path(exists=False), required=True)
@click.option("-om1", "--metadata_output1", help="New format of metadata", type=click.Path(exists=False), required=True)
@click.option("-om2", "--metadata_output2", help="Old format of metadata", type=click.Path(exists=False), required=True)
def main(lmin, lmax, xambig, gisaid_sequences, gisiad_metadata, sample_lineage, country, region, fasta_output,
         metadata_output1, metadata_output2):
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
    df_gisiad = pd.read_table(gisiad_metadata)
    # Rename columns according to column_names
    df_gisiad.columns = column_names
    # Reformat sampling date
    df_gisiad['date'] = df_gisiad['date'].apply(format_date)

    # Extract details of location into separate column
    df_locations = df_gisiad['location'].str.split(r'\s*/\s*', n=3, expand=True)
    df_locations.columns = ['region', 'country', 'division', 'city']
    df_locations = df_locations.astype('category')
    # add extracted location info to output DF
    df_gisiad_metadata = pd.concat([df_gisiad, df_locations], axis=1)

    # Filter sequences
    if country != '' and region != '':
        df_subset = df_gisiad_metadata.loc[((df_gisiad_metadata['pango lineage'] == sample_lineage) &
                                            df_gisiad_metadata['location'].str.contains(region) & df_gisiad_metadata[
                                                'location'].str.contains(country)), :]
    elif country == '' and region != '':
        df_subset = df_gisiad_metadata.loc[((df_gisiad_metadata['pango lineage'] == sample_lineage) &
                                            df_gisiad_metadata['location'].str.contains(region)), :]
    elif country != '' and region == '':
        df_subset = df_gisiad_metadata.loc[((df_gisiad_metadata['pango lineage'] == sample_lineage) &
                                            df_gisiad_metadata['location'].str.contains(country)), :]
    elif country == '' and region == '':
        df_subset = df_gisiad_metadata.loc[(df_gisiad_metadata['pango lineage'] == sample_lineage), :]

    strains_of_interest = set(df_subset['strain'])

    if len(strains_of_interest) > 0:
        with open(gisaid_sequences) as fin, open(fasta_output, 'w') as fout:
            for strains, seq in SimpleFastaParser(fin):
                if '|' in strains:
                    strains = strains.split('|')[0]
                if strains not in strains_of_interest:
                    continue
                if lmin < len(seq) <= lmax and count_ambig_nt(seq) < xambig:
                    fout.write(f'>{strains}\n{seq}\n')
                else:
                    df_subset.drop(df_subset.loc[df_subset['strain'] == strains].index, inplace=True)

        # Keep the current format of metadata
        df_subset.to_csv(metadata_output1, index=False)
        # Save to metadata for nextstrain analysis, drop unnecessary columns
        df_short_subset = df_subset.drop(columns=["location",
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
        df_short_subset['region_exposure'] = df_short_subset['region']
        df_short_subset['country_exposure'] = df_short_subset['country']
        df_short_subset['division_exposure'] = df_short_subset['division']
        df_short_subset.to_csv(metadata_output2, index=False)
    else:
        logging.basicConfig(format='%(message)s',
                            datefmt='[%Y-%m-%d %X]',
                            level=logging.WARNING,
                            handlers=[RichHandler(rich_tracebacks=True,
                                                  tracebacks_show_locals=True)])
        log = logging.getLogger("rich")
        log.warning("No Interest Strains Found!")


if __name__ == '__main__':
    main()
