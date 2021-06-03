
params.options    = [:]
include { MAFFT_MSA } from '../../modules/nf-core/software/mafft/main'          addParams( options: params.options    )
include { NEXTALIGN_MSA } from '../../modules/nf-core/software/nextalign/main'  addParams( options: params.options    )

workflow MSA_MAFFT {
    take:
    ch_consensus_sequences

    main:
    MAFFT_MSA (ch_consensus_sequences, params.reference_fasta)

    emit:
    msa = MAFFT_MSA.out.fasta
}

workflow MSA_NEXTALIGN {
    take:
    ch_consensus_sequences
    ch_ref_sequence

    main:
    NEXTALIGN_MSA (ch_consensus_sequences, ch_ref_sequence)

    emit:
    msa = NEXTALIGN_MSA.out.fasta
}