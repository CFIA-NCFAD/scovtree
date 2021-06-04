params.options    = [:]
include { METADATA_SHIPTV } from '../../modules/local/prepare_metadata_shiptv'  addParams( options: params.options    )

workflow SHIPTV_METADATA{
    take:
    ch_newick
    ch_lineage_report

    main:
    METADATA_SHIPTV (ch_newick, ch_lineage_report)

    emit:
    leaflist           = METADATA_SHIPTV.out.leaflist
    metadata           = METADATA_SHIPTV.out.metadata
}