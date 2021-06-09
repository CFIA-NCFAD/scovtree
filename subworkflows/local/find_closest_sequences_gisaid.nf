
params.options    = [:]
include { FILTERS_GISAID } from '../../modules/local/filters_gisaid'  addParams( options: params.options    )

workflow GISAID_FILTERS {
    take:
    ch_gisaid_sequences
    ch_gisaid_metadata
    ch_lineage_report
    main:
    FILTERS_GISIAD (ch_gisaid_sequences, ch_gisaid_metadata, ch_lineage_report)

    emit:
    sequences   = FILTERS_GISAID.out.fasta
    metadata_1  = FILTERS_GISAID.out.metadata_1
    metadata_2  = FILTERS_GISAID.out.metadata_1
}