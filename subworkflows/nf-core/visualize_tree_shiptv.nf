
params.options    = [:]
include { SHIPTV_VISUALIZATION } from '../../modules/nf-core/software/shiptv/main'  addParams( options: params.options    )

workflow VISUALIZATION_SHIPTV {
    take:
    ch_newick
    ch_leaflist
    ch_metadata

    main:

    SHIPTV_VISUALIZATION (ch_newick, ch_leaflist, ch_metadata)
}