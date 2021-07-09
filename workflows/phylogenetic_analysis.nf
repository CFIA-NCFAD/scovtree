// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()

include { MAFFT } from '../modules/local/mafft' addParams( options: modules['mafft'] )
include { PREPARE_INPUT_SEQUENCES}  from '../modules/local/prepare_input_sequences' addParams( options: modules['prepare_input_sequences'] )
include { AA_MUTATION_MATRIX } from '../modules/local/aa_mutation_matrix' addParams( options: modules['aa_mutation_matrix'] )
include { IQTREE } from '../modules/local/iqtree' addParams( options: modules['iqtree'] )
include { ALIGN2ALLELES } from '../modules/local/align2alleles' addParams( options: modules['align2alleles'] )
include { PANGOLIN } from '../modules/local/pangolin'
include { NEXTCLADE } from '../modules/local/nextclade'
include { PHYLOGENETICTREE_SNPS } from '../modules/local/phylogenetictree_snps' addParams( options: modules['phylogenetictree_snps'] )
include { SHIPTV_METADATA } from '../modules/local/shiptv_metadata' addParams( options: modules['shiptv_metadata'] )
include { SHIPTV } from '../modules/local/shiptv'
include { GET_SOFTWARE_VERSIONS } from '../modules/local/get_software_versions'

workflow PHYLOGENETIC_ANALYSIS {
  ch_software_versions = Channel.empty()

  ch_input             = Channel.fromPath(params.input)
  ch_ref_sequence      = Channel.fromPath(params.reference_fasta)

  PREPARE_INPUT_SEQUENCES(ch_input)

  PANGOLIN(PREPARE_INPUT_SEQUENCES.out.fasta)
  ch_software_versions = ch_software_versions.mix(PANGOLIN.out.version.ifEmpty(null))
  
  MAFFT(
      PREPARE_INPUT_SEQUENCES.out.fasta,
      ch_ref_sequence
  )
  ch_software_versions = ch_software_versions.mix(MAFFT.out.version.ifEmpty(null))
  
  IQTREE(MAFFT.out.fasta)
  ch_software_versions = ch_software_versions.mix(IQTREE.out.version.ifEmpty(null))

  ch_aa_mutation_matrix = Channel.empty()
  if (!params.skip_nextclade) {
    NEXTCLADE(
        PREPARE_INPUT_SEQUENCES.out.fasta,
        'csv'
    )
    AA_MUTATION_MATRIX(NEXTCLADE.out.csv).set { ch_aa_mutation_matrix }
  }
  SHIPTV_METADATA(
      IQTREE.out.treefile,
      ch_aa_mutation_matrix.ifEmpty([]),
      PANGOLIN.out.report
  )
  SHIPTV(
      IQTREE.out.treefile,
      SHIPTV_METADATA.out.leaflist,
      SHIPTV_METADATA.out.metadata
  )
  ch_software_versions = ch_software_versions.mix(SHIPTV.out.version.ifEmpty(null))
  if (!params.skip_snp_tree) {
    ALIGN2ALLELES(MAFFT.out.fasta)
    PHYLOGENETICTREE_SNPS(
        IQTREE.out.treefile,
        ALIGN2ALLELES.out,
        PANGOLIN.out.report
    )
  }
  GET_SOFTWARE_VERSIONS(ch_software_versions.collect())
}
