params.options    = [:]
include { PRUNE_DOWN_TREE } from '../../modules/local/prune_down_tree'  addParams( options: params.options    )

workflow GET_SUBTREE {
    take:
    ch_newick
    ch_lineage_report
    ch_metadata

    main:
    PRUNE_DOWN_TREE (ch_newick, ch_lineage_report, ch_metadata)

    emit:
    leaflist           = PRUNE_DOWN_TREE.out.leaflist
    metadata           = PRUNE_DOWN_TREE.out.metadata
}