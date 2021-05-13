
params.options    = [:]
include { MAFFT_MSA } from '../../modules/nf-core/software/mafft/main'  addParams( options: params.options    )

workflow MSA_MAFFT {
    take:
    consensus_sequences

    main:
    MAFFT_MSA (consensus_sequences, params.reference_fasta)

    emit:
    msa = MAFFT_MSA.out.fasta
}