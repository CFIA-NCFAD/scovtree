// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()


include { PANGOLIN } from '../modules/local/pangolin'
include { FILTER_GISAID } from '../modules/local/filter_gisaid' addParams( options: modules['filter_gisaid'] )
include { NEXTALIGN } from '../modules/local/nextalign' addParams( options: modules['nextalign'] )
include { FILTER_MSA } from '../modules/local/filter_msa' addParams( options: modules['filter_msa'] )
include { IQTREE } from '../modules/local/iqtree' addParams( options: modules['iqtree'] )
include { PRUNE_TREE } from '../modules/local/prune_tree' addParams( options: modules['prune_tree'] )
include { SEQUENCES_NEXTCLADE } from '../modules/local/sequences_nextclade' addParams( options: modules['sequences_nextclade'] )
include { NEXTCLADE } from '../modules/local/nextclade'
include { AA_MUTATION_MATRIX } from '../modules/local/aa_mutation_matrix' addParams( options: modules['aa_mutation_matrix'] )
include { MERGE_METADATA } from '../modules/local/merge_metadata' addParams( options: modules['merge_metadata'] )
include { SHIPTV } from '../modules/local/shiptv'

workflow PHYLOGENETIC_GISAID {
  ch_software_versions = Channel.empty()

  ch_gisaid_sequences = Channel.fromPath(params.gisaid_sequences)
  ch_gisaid_metadata  = Channel.fromPath(params.gisaid_metadata)
  ch_reference_fasta  = Channel.fromPath(params.reference_fasta)
  ch_input            = Channel.fromPath(params.input)

  PANGOLIN(ch_input)
  ch_software_versions = ch_software_versions.mix(PANGOLIN.out.version.ifEmpty(null))
  
  FILTER_GISAID(
    ch_input,
    ch_gisaid_sequences,
    ch_gisaid_metadata,
    PANGOLIN.out.report
  )
  
  NEXTALIGN(
    FILTER_GISAID.out.fasta,
    ch_reference_fasta
  )
  ch_software_versions = ch_software_versions.mix(NEXTALIGN.out.version.ifEmpty(null))
  
  FILTER_MSA(
    NEXTALIGN.out.fasta,
    PANGOLIN.out.report,
    FILTER_GISAID.out.metadata
  )
  
  IQTREE(FILTER_MSA.out.fasta)
  ch_software_versions = ch_software_versions.mix(IQTREE.out.version.ifEmpty(null))

  PRUNE_TREE(
    IQTREE.out.treefile,
    PANGOLIN.out.report,
    FILTER_MSA.out.metadata
  )

  ch_aa_mutation_matrix = Channel.empty()
  if (!params.skip_nextclade) {
    SEQUENCES_NEXTCLADE(
      PRUNE_TREE.out.metadata,
      FILTER_GISAID.out.fasta,
      PANGOLIN.out.report
    )
    NEXTCLADE(SEQUENCES_NEXTCLADE.out, 'csv')
    ch_software_versions = ch_software_versions.mix(NEXTCLADE.out.version.ifEmpty(null))
    AA_MUTATION_MATRIX(NEXTCLADE.out.csv)
    AA_MUTATION_MATRIX.out.set { ch_aa_mutation_matrix }
  }
  MERGE_METADATA(
    PRUNE_TREE.out.metadata,
    ch_aa_mutation_matrix.ifEmpty([]),
    PANGOLIN.out.report
  )
  SHIPTV(
    IQTREE.out.treefile,
    PRUNE_TREE.out.leaflist,
    MERGE_METADATA.out
  )
  ch_software_versions = ch_software_versions.mix(SHIPTV.out.version.ifEmpty(null))
  // TODO: output software versions to TSV
}
