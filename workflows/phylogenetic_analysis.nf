// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()

def msa_align_options              = modules['msa_mafft']
def iqtree_options                 = modules['phylogenetic_iqtree']
def pangolin_options               = modules['pangolin']
def alleles_options                = modules['alleles']
def tree_snps_options              = modules['tree_snps']
def reroot_tree_options            = modules['reroot_tree']
def shiptv_tree_options            = modules['shiptv_visualization']
def nextclade_options              = modules['nextclade']


include { MAFFT_MSA                } from '../modules/nf-core/software/mafft/main'                      addParams ( options: msa_align_options            )
include { IQTREE_PHYLOGENETICTREE  } from '../modules/nf-core/software/iqtree/main'                     addParams ( options: iqtree_options               )
include { DETERMINE_SNPS           } from '../modules/local/determine_snps'                             addParams ( options: alleles_options              )
include { PANGOLIN_LINEAGES        } from '../modules/nf-core/software/pangolin/main'                   addParams ( options: pangolin_options             )
include { PHYLOGENETICTREE_SNPS    } from '../modules/local/phylogenetictree_snps'                      addParams ( options: tree_snps_options            )
include { NEXTCLADE                } from '../modules/nf-core/software/nextclade/main'                  addParams ( options: nextclade_options            )
include { AA_SUBSTITUTION_CHANGE   } from '../modules/local/aa_sub_nextclade'                           addParams ( options: nextclade_options            )
include { SHIPTV_METADATA          } from '../modules/local/shiptv_metadata'                            addParams ( options: shiptv_tree_options          )
include { SHIPTV_VISUALIZATION     } from '../modules/nf-core/software/shiptv/main'                     addParams ( options: shiptv_tree_options          )


workflow PHYLOGENETIC_ANALYSIS {

    ch_consensus_seqs   = Channel.fromPath(params.input)
    ch_ref_sequence     = Channel.fromPath(params.reference_fasta)

    MAFFT_MSA               (ch_consensus_seqs, ch_ref_sequence)
    IQTREE_PHYLOGENETICTREE (MAFFT_MSA.out.fasta)
    DETERMINE_SNPS          (MAFFT_MSA.out.fasta)
    PANGOLIN_LINEAGES       (ch_consensus_seqs)
    PHYLOGENETICTREE_SNPS   (IQTREE_PHYLOGENETICTREE.out.treefile, DETERMINE_SNPS.out.alleles, PANGOLIN_LINEAGES.out.report)
    NEXTCLADE               (ch_consensus_seqs,'csv')
    AA_SUBSTITUTION_CHANGE  (NEXTCLADE.out.csv)
    SHIPTV_METADATA         (IQTREE_PHYLOGENETICTREE.out.treefile, AA_SUBSTITUTION_CHANGE.out.tsv, PANGOLIN_LINEAGES.out.report)
    SHIPTV_VISUALIZATION    (IQTREE_PHYLOGENETICTREE.out.treefile, SHIPTV_METADATA.out.leaflist, SHIPTV_METADATA.out.metadata)

}