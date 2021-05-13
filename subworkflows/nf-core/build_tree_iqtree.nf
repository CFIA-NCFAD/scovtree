
params.options    = [:]
include { IQTREE_PHYLOGENETICTREE } from '../../modules/nf-core/software/iqtree/main'  addParams( options: params.options    )

workflow PHYLOGENETICTREE_IQTREE {
    take:
    msa_fasta

    main:
    IQTREE_PHYLOGENETICTREE (msa_fasta)

    emit:
    treefile = IQTREE_PHYLOGENETICTREE.out.treefile

}