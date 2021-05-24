
params.options    = [:]
include { FILTERS_GISIAD } from '../../modules/local/filters_gisiad'  addParams( options: params.options    )

workflow GISIAD_FILTERS {
    take:
    ch_gisiad_sequences
    ch_gisiad_metadata
    ch_lineage_report
    main:
    FILTERS_GISIAD (ch_gisiad_sequences, ch_gisiad_metadata, ch_lineage_report)

    emit:
    sequences   = FILTERS_GISIAD.out.fasta
    metadata_1  = FILTERS_GISIAD.out.metadata_1
    metadata_2  = FILTERS_GISIAD.out.metadata_1
}