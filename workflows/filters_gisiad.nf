// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()

def msa_mafft_options     = modules['msa_mafft']
def msa_nextalign_options = modules['msa_nextalign']
def iqtree_options        = modules['phylogenetic_iqtree']
def pangolin_options      = modules['pangolin']
def alleles_options       = modules['alleles']
def tree_snps_options     = modules['tree_snps']
def reroot_tree_options   = modules['reroot_tree']
def shiptv_tree_options   = modules['shiptv']
def filter_gisiad_options = modules['filters_gisiad']
def filter_msa_options    = modules['filters_msa']
def get_subtree_options   = modules['subtree']

include { MSA_MAFFT                }   from '../subworkflows/nf-core/multiple_sequence_alignment'        addParams ( options: msa_mafft_options       )
include { MSA_NEXTALIGN            }   from '../subworkflows/nf-core/multiple_sequence_alignment'        addParams ( options: msa_nextalign_options   )
include { PHYLOGENETICTREE_IQTREE  }   from '../subworkflows/nf-core/build_tree_iqtree'                  addParams ( options: iqtree_options          )
include { LINEAGES_PANGOLIN        }   from '../subworkflows/nf-core/assign_lineages_pangolin'           addParams ( options: pangolin_options        )
include { ALLELES                  }   from '../subworkflows/local/alleles'                              addParams ( options: alleles_options         )
include { VISUALIZATION_TREE_SNPS  }   from '../subworkflows/local/visualize_tree_snps'                  addParams ( options: tree_snps_options       )
include { REROOT_TREE              }   from '../subworkflows/nf-core/reroot_tree'                        addParams ( options: reroot_tree_options     )
include { VISUALIZATION_SHIPTV     }   from '../subworkflows/nf-core/visualize_tree_shiptv'              addParams ( options: shiptv_tree_options     )
include { GISIAD_FILTERS           }   from '../subworkflows/local/find_closest_sequences_gisiad'        addParams ( options: filter_gisiad_options   )
include { SEQUENCES_CAT            }   from '../subworkflows/nf-core/cat_sequences'
include { FILTER_10K_STRAINS       }   from '../subworkflows/local/find_10K_strain'                      addParams ( options: filter_msa_options      )
include { GET_SUBTREE              }   from '../subworkflows/local/get_subtree'                          addParams ( options: get_subtree_options     )

workflow FILTERS_GISIAD {

    ch_gisiad_sequences = Channel.fromPath(params.gisiad_sequences)
    ch_gisiad_metadata  = Channel.fromPath(params.gisiad_metadata)
    ch_consensus_seqs   = Channel
    .fromPath(params.input)
    .splitFasta( record: [id: true, sequence: true])
    .collectFile( name: 'consensus_seqs.fa' ){
    ">${it.id}\n${it.sequence}"
    }
    LINEAGES_PANGOLIN       (ch_consensus_seqs)
    GISIAD_FILTERS          (ch_gisiad_sequences, ch_gisiad_metadata, LINEAGES_PANGOLIN.out.report)
    SEQUENCES_CAT           (GISIAD_FILTERS.out.sequences, ch_consensus_seqs)
    MSA_NEXTALIGN           (SEQUENCES_CAT.out.merged_sequences)
    FILTER_10K_STRAINS      (MSA_NEXTALIGN.out.msa, LINEAGES_PANGOLIN.out.report, GISIAD_FILTERS.out.metadata_1)
    PHYLOGENETICTREE_IQTREE (FILTER_10K_STRAINS.out.msa_filtered)
    GET_SUBTREE             (PHYLOGENETICTREE_IQTREE.out.treefile, LINEAGES_PANGOLIN.out.report, FILTER_10K_STRAINS.out.metadata_filtered)
    VISUALIZATION_SHIPTV    (PHYLOGENETICTREE_IQTREE.out.treefile, GET_SUBTREE.out.leaflist, GET_SUBTREE.out.metadata)
}