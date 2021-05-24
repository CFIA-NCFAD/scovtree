
params.options    = [:]
include { PANGOLIN_LINEAGES } from '../../modules/nf-core/software/pangolin/main'  addParams( options: params.options    )

workflow LINEAGES_PANGOLIN{
    take:
    ch_fasta

    main:
    PANGOLIN_LINEAGES (ch_fasta)

    emit:
    report = PANGOLIN_LINEAGES.out.report

}