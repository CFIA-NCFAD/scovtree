
params.options    = [:]
include { PANGOLIN_LINEAGES } from '../../modules/nf-core/software/pangolin/main'  addParams( options: params.options    )

workflow LINEAGES_PANGOLIN{
    take:
    fasta

    main:
    PANGOLIN_LINEAGES (fasta)

    emit:
    report = PANGOLIN_LINEAGES.out.report

}