// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()

def msa_align_options     = modules['msa_mafft']
def iqtree_options        = modules['phylogenetic_iqtree']
def pangolin_options      = modules['pangolin']
def alleles_options       = modules['alleles']
def tree_snps_options     = modules['tree_snps']
def reroot_tree_options   = modules['reroot_tree']
def shiptv_tree_options   = modules['shiptv']
def filter_gisiad_options = modules['filters_gisiad']

include { MSA_MAFFT                }   from '../subworkflows/nf-core/multiple_sequence_alignment'        addParams ( options: msa_align_options       )
include { PHYLOGENETICTREE_IQTREE  }   from '../subworkflows/nf-core/build_tree_iqtree'                  addParams ( options: iqtree_options          )
include { LINEAGES_PANGOLIN        }   from '../subworkflows/nf-core/assign_lineages_pangolin'           addParams ( options: pangolin_options        )
include { ALLELES                  }   from '../subworkflows/local/alleles'                              addParams ( options: alleles_options         )
include { VISUALIZATION_TREE_SNPS  }   from '../subworkflows/local/visualize_tree_snps'                  addParams ( options: tree_snps_options       )
include { REROOT_TREE              }   from '../subworkflows/nf-core/reroot_tree'                        addParams ( options: reroot_tree_options     )
include { VISUALIZATION_SHIPTV     }   from '../subworkflows/nf-core/visualize_tree_shiptv'              addParams ( options: shiptv_tree_options     )
include { GISIAD_FILTERS           }   from '../subworkflows/local/find_closest_sequences_gisiad'        addParams ( options: filter_gisiad_options   )

workflow FILTERS_GISIAD {

    GISIAD_FILTERS()
    MSA_MAFFT               (GISIAD_FILTERS.out.sequences)
    PHYLOGENETICTREE_IQTREE (MSA_MAFFT.out.msa)
    REROOT_TREE             (PHYLOGENETICTREE_IQTREE.out.treefile)
    ALLELES                 (MSA_MAFFT.out.msa)
    LINEAGES_PANGOLIN       (GISIAD_FILTERS.out.sequences)
    VISUALIZATION_TREE_SNPS (REROOT_TREE.out.newick_treefile, ALLELES.out.alleles, LINEAGES_PANGOLIN.out.report)
    VISUALIZATION_SHIPTV    (REROOT_TREE.out.newick_treefile)

}