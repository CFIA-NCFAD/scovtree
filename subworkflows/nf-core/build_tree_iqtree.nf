
params.options    = [:]
include { IQTREE_PHYLOGENETICTREE } from '../../modules/nf-core/software/iqtree/main'  addParams( options: params.options    )

workflow PHYLOGENETICTREE_IQTREE {
    take:
    ch_msa_fasta

    main:
    IQTREE_PHYLOGENETICTREE (ch_msa_fasta)

    emit:
    treefile = IQTREE_PHYLOGENETICTREE.out.treefile

}