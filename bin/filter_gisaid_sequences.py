#!/usr/bin/env python3
import logging
import click
import pandas as pd
from Bio.SeqIO.FastaIO import SimpleFastaParser
from collections import Counter
from typing import Iterator, Tuple
import tarfile


def count_ambig_nt(seq: str) -> int:
    counter = Counter(seq.lower())
    return sum(v for k, v in counter.items() if k not in {'a', 'g', 'c', 't', '-'})


def read_fasta_tarxz(tarxz_path) -> Iterator[Tuple[str, str]]:
    # Skip any text before the first record (e.g. blank lines, comments)
    with tarfile.open(tarxz_path) as tar:
        fasta_path = list(n for n in tar.getnames() if n.endswith('.fasta'))[0]
        handle = tar.extractfile(fasta_path)
        for line in handle:
            line = line.decode()
            if line[0] == ">":
                title = line[1:].rstrip()
                break
            else:
                # no break encountered - probably an empty file
                return
        lines = []
        for line in handle:
            line = line.decode()
            if line[0] == ">":
                yield title, "".join(lines).replace(" ", "").replace("\r", "")
                lines = []
                title = line[1:].rstrip()
                continue
            lines.append(line.rstrip())
        yield title, "".join(lines).replace(" ", "").replace("\r", "")


def format_date(sampling_date: str) -> str:
    if '-' not in sampling_date:  # contain year only
        return sampling_date + '-XX-XX'  # 2020-XX-XX
    else:
        sampling_date_list = sampling_date.split('-')
        if len(sampling_date_list) == 2:
            return sampling_date + '-XX'  # 2020-02-XX
        elif len(sampling_date_list) == 3:
            return sampling_date  # 2020-02-01


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
@click.option("-i", "--gisaid-sequences", type=click.Path(exists=True), required=True)
@click.option("-m", "--gisaid-metadata", type=click.Path(exists=True), required=True)
@click.option("-R", "--lineage-report", type=click.Path(exists=True), required=False, default='')
@click.option("-s", "--sample_lineage", type=str, required=True, default='')
@click.option("-c", "--country", help="Country", required=False, type=str, default='')
@click.option("-r", "--region", help="Region", required=False, type=str, default='')
@click.option("-of", "--fasta-output", type=click.Path(exists=False), required=True)
@click.option("-fm", "--filtered-metadata", help="Filtered metadata", type=click.Path(exists=False), required=True)
@click.option("-nm", "--nextstrain-metadata", help="Metadata for nextstrain analysis", type=click.Path(exists=False), required=True)
@click.option("-ot", "--statistics-output", help="Statistics output", type=click.Path(exists=False), required=True)
def main(lmin, lmax, xambig, gisaid_sequences, gisaid_metadata, lineage_report, sample_lineage, country, region,
         fasta_output, filtered_metadata, nextstrain_metadata, statistics_output):

    lineage = ''
    if lineage_report != '':
        df_lineage_report = pd.read_table(lineage_report, sep=',')
        df_lineage_report.drop_duplicates(subset=['lineage'], inplace=True)
        lineage = df_lineage_report['lineage']
    else:
        lineage = [sample_lineage]

    # Parse gisaid metadata into dataframe
    if tarfile.is_tarfile(gisaid_metadata):
        with tarfile.open(gisaid_metadata, "r:*") as tar:
            csv_path = list(n for n in tar.getnames() if n.endswith('.tsv'))[0]
            df_gisaid = pd.read_table(tar.extractfile(csv_path))
    else:
        df_gisaid = pd.read_table(gisaid_metadata)

    #Replace space in columns name by _
    df_gisaid.columns = df_gisaid.columns.str.replace(' ', '_')

    # Reformat strain name
    df_gisaid['Virus_name'] = df_gisaid['Virus_name'].apply(format_strain_name)

    # Extract details of location into separate column
    df_locations = df_gisaid['Location'].str.split(r'\s*/\s*', n=3, expand=True)
    df_locations.columns = ['region', 'country', 'division', 'city']
    df_locations = df_locations.astype('category')
    # add extracted location info to output DF
    df_gisaid_metadata = pd.concat([df_gisaid, df_locations], axis=1)

    # df_gisaid_metadata.drop_duplicates(subset=['strain'], inplace=True)

    # Filter sequences
    # lineages is a set of lineage strings
    mask = df_gisaid_metadata['Pango_lineage'].isin(lineage)
    if country:
        mask = mask & df_gisaid_metadata['Location'].str.contains(country)
    if region:
        mask = mask & df_gisaid_metadata['Location'].str.contains(region)
    df_subset = df_gisaid_metadata.loc[mask, :]

    num_lineage_found = df_subset.shape[0]
    # Drop rows have duplicate strain names
    # df_subset.drop_duplicates(subset = ['strain'], inplace = True)
    strains_of_interest = set(df_subset['Virus_name'])

    strains_of_interest_dict = {}
    for vname in strains_of_interest:
        if not strains_of_interest_dict.get(vname):
            strains_of_interest_dict[vname] = vname

    len_strains_of_interest = len(strains_of_interest)
    num_seqs_found = 0
    if len(strains_of_interest) > 0:

        added_strains = {}
        df_filtered = pd.DataFrame(columns = df_gisaid.columns)

        with open(fasta_output, 'w') as fout:
            if tarfile.is_tarfile(gisaid_sequences):
                for strains, seq in read_fasta_tarxz(gisaid_sequences):
                    if '|' in strains:
                        strains = strains.split('|')[0]
                    if ' ' in strains:
                        strains = strains.replace(' ', '_')
                    #if strains not in strains_of_interest:
                        #continue
                    if not strains_of_interest_dict.get(strains):
                        continue
                    if (lmin < len(seq) <= lmax) and (count_ambig_nt(seq) < xambig) and (not added_strains.get(strains)):
                        num_seqs_found = num_seqs_found + 1
                        added_strains[strains] = strains
                        # Get metadata information
                        row_index = df_subset.loc[df_subset['Virus_name'] == strains].index
                        df_filtered = df_filtered.append(df_subset.loc[row_index])
                        # Write sequences
                        fout.write(f'>{strains}\n{seq}\n')
            else:
                with open(gisaid_sequences) as fin:
                    for strains, seq in SimpleFastaParser(fin):
                        if '|' in strains:
                            strains = strains.split('|')[0]
                        if ' ' in strains:
                            strains = strains.replace(' ', '_')
                        #if strains not in strains_of_interest:
                            #continue
                        if not strains_of_interest_dict.get(strains):
                            continue
                        if (lmin < len(seq) <= lmax) and (count_ambig_nt(seq) < xambig) and (not added_strains.get(strains)):
                            num_seqs_found = num_seqs_found + 1
                            added_strains[strains] = strains
                            # Get metadata information
                            row_index = df_subset.loc[df_subset['Virus_name'] == strains].index
                            df_filtered = df_filtered.append(df_subset.loc[row_index])
                            # Write sequences
                            fout.write(f'>{strains}\n{seq}\n')

        # Keep the current format of metadata
        df_filtered.to_csv(filtered_metadata, sep='\t', index=False)

        # Save to metadata for nextstrain analysis, drop unnecessary columns
        df_subset_filtered = df_filtered.drop(columns=["Location",
                                                       "Additional_location_information",
                                                       "Sequence_length",
                                                       "Host",
                                                       "Patient_age",
                                                       "Gender",
                                                       "Clade",
                                                       "Pango_lineage",
                                                       "Pangolin_version",
                                                       "Variant",
                                                       "AA_Substitutions",
                                                       "Submission_date",
                                                       "Is_reference?",
                                                       "Is_complete?",
                                                       "Is_high_coverage?",
                                                       "Is_low_coverage?",
                                                       "N-Content",
                                                       "GC-Content"])
        # Need to specify exposure location as we specify country
        # The information missed in metadata so set them as the same as location information
        df_subset_filtered['region_exposure'] = df_subset_filtered['region']
        df_subset_filtered['country_exposure'] = df_subset_filtered['country']
        df_subset_filtered['division_exposure'] = df_subset_filtered['division']
        df_subset_filtered.to_csv(nextstrain_metadata, sep='\t', index=False)
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
