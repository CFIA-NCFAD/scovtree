
params.options    = [:]
include { FILTERS_GISIAD } from '../../modules/local/filters_gisiad'  addParams( options: params.options    )

workflow GISIAD_FILTERS {

    main:
    FILTERS_GISIAD (params.gisiad_sequences, params.gisiad_metadata)

    emit:
    sequences = FILTERS_GISIAD.out.gisiad_sequences
    metadata  = FILTERS_GISIAD.out.gisiad_metadata

}