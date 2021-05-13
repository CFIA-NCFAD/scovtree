
params.options    = [:]
include { SHIPTV_VISUALIZATION } from '../../modules/nf-core/software/shiptv/main'  addParams( options: params.options    )

workflow VISUALIZATION_SHIPTV {
    take:
    newick

    main:
    SHIPTV_VISUALIZATION (newick)
}