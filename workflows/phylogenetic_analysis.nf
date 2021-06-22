// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()

include { MAFFT } from '../modules/local/mafft' addParams( options: modules['mafft'] )
include { AA_MUTATION_MATRIX } from '../modules/local/aa_mutation_matrix' addParams( options: modules['aa_mutation_matrix'] )
include { IQTREE } from '../modules/local/iqtree' addParams( options: modules['iqtree'] )

include { ALIGN2ALLELES } from '../modules/local/align2alleles' addParams( options: modules['align2alleles'] )
include { PANGOLIN } from '../modules/local/pangolin' addParams( options: modules['pangolin'] )
include { NEXTCLADE } from '../modules/local/nextclade' addParams( options: modules['nextclade'] )
include { PHYLOGENETICTREE_SNPS } from '../modules/local/phylogenetictree_snps' addParams( options: modules['phylogenetictree_snps'] )
include { SHIPTV_METADATA } from '../modules/local/shiptv_metadata' addParams( options: modules['shiptv_metadata'] )
include { SHIPTV } from '../modules/local/shiptv' addParams( options: modules['shiptv'] )

workflow PHYLOGENETIC_ANALYSIS {
  ch_consensus_seqs   = Channel.fromPath(params.input)
  ch_ref_sequence     = Channel.fromPath(params.reference_fasta)

  MAFFT(
      ch_consensus_seqs,
      ch_ref_sequence
  )
  IQTREE(MAFFT.out.fasta)
  ALIGN2ALLELES(MAFFT.out.fasta)
  PANGOLIN(ch_consensus_seqs)
  PHYLOGENETICTREE_SNPS(
      IQTREE.out.treefile,
      ALIGN2ALLELES.out,
      PANGOLIN.out.report
  )
  NEXTCLADE(
      ch_consensus_seqs,
      'csv'
  )
  AA_MUTATION_MATRIX(NEXTCLADE.out.csv)
  SHIPTV_METADATA(
      IQTREE.out.treefile,
      AA_MUTATION_MATRIX.out,
      PANGOLIN.out.report
  )
  SHIPTV(
      IQTREE.out.treefile,
      SHIPTV_METADATA.out.leaflist,
      SHIPTV_METADATA.out.metadata
  )
}
