// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()

def msa_mafft_options              = modules['msa_mafft']
def msa_nextalign_options          = modules['msa_nextalign']
def iqtree_options                 = modules['phylogenetic_iqtree']
def pangolin_options               = modules['pangolin']
def alleles_options                = modules['alleles']
def tree_snps_options              = modules['tree_snps']
def shiptv_visualization_options   = modules['shiptv_visualization']
def merge_metadata_options         = modules['merge_metadata']
def filter_gisaid_options          = modules['filter_gisaid']
def filter_msa_options             = modules['filter_msa']
def get_subtree_options            = modules['subtree']
def nextclade_options              = modules['nextclade']

include { PANGOLIN_LINEAGES       } from '../modules/nf-core/software/pangolin/main'   addParams( options: pangolin_options             )
include { NEXTALIGN_MSA           } from '../modules/nf-core/software/nextalign/main'  addParams( options: msa_nextalign_options        )
include { CAT_SEQUENCES           } from '../modules/nf-core/software/cat/main'
include { FILTERS_GISAID          } from '../modules/local/filter_gisaid'              addParams( options: filter_gisaid_options        )
include { FILTERS_MSA             } from '../modules/local/filter_msa'                 addParams( options: filter_msa_options           )
include { IQTREE_PHYLOGENETICTREE } from '../modules/nf-core/software/iqtree/main'     addParams( options: iqtree_options               )
include { SHIPTV_VISUALIZATION    } from '../modules/nf-core/software/shiptv/main'     addParams( options: shiptv_visualization_options )
include { MERGE_METADATA          } from '../modules/local/merge_metadata'             addParams( options: merge_metadata_options       )
include { PRUNE_DOWN_TREE         } from '../modules/local/prune_down_tree'            addParams( options: get_subtree_options          )
include { SEQUENCES_NEXTCLADE     } from '../modules/local/get_sequences_nextclade'    addParams( options: nextclade_options            )
include { NEXTCLADE               } from '../modules/nf-core/software/nextclade/main'  addParams( options: nextclade_options            )
include { AA_SUBSTITUTION_CHANGE  } from '../modules/local/aa_sub_nextclade'           addParams( options: nextclade_options            )


workflow PHYLOGENETIC_GISAID {

    ch_gisaid_sequences = Channel.fromPath(params.gisaid_sequences)
    ch_gisaid_metadata  = Channel.fromPath(params.gisaid_metadata)
    ch_ref_sequence     = Channel.fromPath(params.reference_fasta)
    ch_consensus_seqs   = Channel.fromPath(params.input)

    PANGOLIN_LINEAGES         (ch_consensus_seqs)
    FILTERS_GISAID            (ch_gisaid_sequences, ch_gisaid_metadata, PANGOLIN_LINEAGES.out.report)
    CAT_SEQUENCES             (FILTERS_GISAID.out.fasta, ch_consensus_seqs, ch_ref_sequence)
    NEXTALIGN_MSA             (CAT_SEQUENCES.out.merged_sequences, ch_ref_sequence)
    FILTERS_MSA               (NEXTALIGN_MSA.out.fasta, PANGOLIN_LINEAGES.out.report, FILTERS_GISAID.out.filtered_metadata)
    IQTREE_PHYLOGENETICTREE   (FILTERS_MSA.out.fasta)
    PRUNE_DOWN_TREE           (IQTREE_PHYLOGENETICTREE.out.treefile, PANGOLIN_LINEAGES.out.report, FILTERS_MSA.out.metadata)
    SEQUENCES_NEXTCLADE       (PRUNE_DOWN_TREE.out.metadata, CAT_SEQUENCES.out.merged_sequences, PANGOLIN_LINEAGES.out.report)
    NEXTCLADE                 (SEQUENCES_NEXTCLADE.out.fasta, 'csv')
    AA_SUBSTITUTION_CHANGE    (NEXTCLADE.out.csv)
    MERGE_METADATA            (PRUNE_DOWN_TREE.out.metadata, AA_SUBSTITUTION_CHANGE.out.tsv, PANGOLIN_LINEAGES.out.report)
    SHIPTV_VISUALIZATION      (IQTREE_PHYLOGENETICTREE.out.treefile, PRUNE_DOWN_TREE.out.leaflist, MERGE_METADATA.out.metadata)

}