
include { CAT_SEQUENCES } from '../../modules/nf-core/software/cat/main'

workflow SEQUENCES_CAT {
    take:
    ch_filter_gisiad_sequences
    ch_input_sequences

    main:

    CAT_SEQUENCES (ch_filter_gisiad_sequences, ch_input_sequences)

    emit:
    merged_sequences = CAT_SEQUENCES.out.merged_sequences

}