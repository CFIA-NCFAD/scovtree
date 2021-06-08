params.options    = [:]
include { SEQUENCES_NEXTCLADE } from '../../modules/local/get_sequences_nextclade'  addParams( options: params.options    )

workflow NEXTCLADE_SEQUENCES {

    take:
    ch_metadata
    ch_sequences

    main:
    SEQUENCES_NEXTCLADE (ch_metadata, ch_sequences)

    emit:
    sequences  = SEQUENCES_NEXTCLADE.out.fasta
}