
params.options    = [:]
include { PHYLOGENETICTREE_SNPS } from '../../modules/local/phylogenetictree_snps'  addParams( options: params.options    )

workflow VISUALIZATION_TREE_SNPS {
    take:
    newick
    alleles
    lineages

    main:
    PHYLOGENETICTREE_SNPS (newick, alleles, lineages)
}