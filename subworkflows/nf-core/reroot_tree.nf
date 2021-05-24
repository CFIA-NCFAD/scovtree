
params.options    = [:]
include { NW_REROOT } from '../../modules/nf-core/software/newickutils/main'  addParams( options: params.options    )

workflow REROOT_TREE {
    take:
    ch_newick_tree

    main:
    NW_REROOT (ch_newick_tree, params.reference_fasta)

    emit:
    newick_treefile = NW_REROOT.out.newick

}