params.options    = [:]
include { FILTERS_MSA } from '../../modules/local/filter_msa'  addParams( options: params.options    )

workflow FILTER_10K_STRAINS {
    take:
    ch_msa
    ch_lineage_report
    ch_metadata

    main:
    FILTERS_MSA (ch_msa, ch_lineage_report, ch_metadata)

    emit:
    msa_filtered       = FILTERS_MSA.out.fasta
    metadata_filtered  = FILTERS_MSA.out.metadata
}