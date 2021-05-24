#!/usr/bin/env python3
import logging
import click
import pandas as pd
from Bio.SeqIO.FastaIO import SimpleFastaParser
from collections import Counter


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option("-i", "--msa_sequences", help="Multiple Sequence Alignment", type=click.Path(exists=True), required=False)
@click.option("-M", "--metadata_input",
              help="Metadata of Multiple Sequence Alignment (It is a metadata file after gisaid filtering step)",
              type=click.Path(exists=True), required=False)
@click.option("-r", "--lineage_report", help="Pangolin report of input sequences", type=click.Path(exists=False),
              required=False, default='')
@click.option("-R", "--ref_name", help="Name of reference sequence", required=False, type=str, default='MN908947.3')
@click.option("-a", "--avg_sequences", help="Maximum of sequences after filtering", required=False, type=int,
              default=10000)
# @click.option("-g", "--gaps", help="Maximum of gaps in Seq", required=False, type=int, default=121)
# @click.option("-n", "--N", help="Maximum of N", required=False, type=int, default=441)
@click.option("-o", "--fasta_output", help="Miltiple Sequence Alignment after filtering", type=click.Path(exists=False),
              required=False)
@click.option("-m", "--metadata_output", help="Metadata file of Multiple Sequence Alignment after filtering ",
              type=click.Path(exists=False), required=False)
def main(msa_sequences, metadata_input, lineage_report, ref_name, avg_sequences, fasta_output, metadata_output):
    # Read Metadata of Multiple Sequence Alignment
    df_metadata_msa = pd.read_table(metadata_input, sep='\t')
    df_metadata_output = pd.DataFrame(columns = df_metadata_msa.columns)

    # df_input_metadata = pd.read_table(lineage_report, sep='\t')
    df_lineage_report = pd.read_table(lineage_report, sep=',')

    # Reference and input strains must be kept
    input_sequences_strains = df_lineage_report['taxon'].tolist()
    input_sequences_strains.append(ref_name)

    # Keep 1 representative sequence however keep it if it is same as Canada sequences or input_sequences_strains
    seq_strain_dict = {}
    drop = 0
    with open(msa_sequences) as fin:
        for strains, seq in SimpleFastaParser(fin):
            if strains in input_sequences_strains or 'Canada' in strains:
                if seq_strain_dict.get(seq):
                    if strains not in seq_strain_dict[seq]:
                        seq_strain_dict[seq].append(strains)
                else:
                    seq_strain_dict[seq] = []
                    seq_strain_dict[seq].append(strains)
            else:
                if seq_strain_dict.get(seq):
                    if strains not in seq_strain_dict[seq]:
                        value = seq_strain_dict[seq]
                        for values in value:
                            if ('Canada' in values) or (values in input_sequences_strains):
                                seq_strain_dict[seq].append(strains)
                                break
                    continue
                else:
                    seq_strain_dict[seq] = []
                    seq_strain_dict[seq].append(strains)

    # Sequence records
    seq_recs = []
    for seq_key, strains_value in seq_strain_dict.items():
        seq_key = seq_key.upper()
        seq_nt = sum(seq_key.count(x) for x in list('AGCT'))
        skip = False
        if any('Canada' in values for values in strains_value) or any(item in input_sequences_strains for item in strains_value) :
            skip = True
        seq_recs.append(dict(strain=strains_value,
                             seq_n=seq_key.count('N'),
                             seq_gap=seq_key.count('-'),
                             seq_nt=seq_nt,
                             skip_strains=skip, ))
    df_seq_recs = pd.DataFrame(seq_recs)
    # Create skip strains
    df_skip_strains = df_seq_recs[df_seq_recs['skip_strains'] == True]

    skip_strains = (df_skip_strains['strain']).tolist()

    df_less_n_gaps = df_seq_recs.query('seq_n <= 60 and seq_gap <= 121')

    sampled_strains = df_less_n_gaps.strain.sample(n=(avg_sequences - len(df_skip_strains))).tolist()

    for item in skip_strains:
        if item not in sampled_strains:
            sampled_strains.append(item)

    with open(fasta_output, 'w') as fout:
        for seq_key, strains_value in seq_strain_dict.items():
            for strains_list in sampled_strains:
                if strains_value == strains_list:
                    for strain in strains_list:
                        row_index = df_metadata_msa.loc[df_metadata_msa['strain'] == strain].index
                        df_metadata_output = df_metadata_output.append(df_metadata_msa.loc[row_index])
                        fout.write(f'>{strain}\n{seq_key}\n')
                    break
    df_metadata_output.to_csv(metadata_output, sep='\t', index=False)

if __name__ == '__main__':
    main()
