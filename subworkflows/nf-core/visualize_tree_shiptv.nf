
params.options    = [:]
include { SHIPTV_VISUALIZATION } from '../../modules/nf-core/phylogenetictree_snps'  addParams( options: params.options    )

workflow VISUALIZATION_TREE_SNPS {
    take:
    newick
    alleles
    lineages

    main:
    PHYLOGENETICTREE_SNPS (newick, alleles, lineages)
}