// Don't overwrite global params.modules, create a copy instead and use that within the main script.
def modules = params.modules.clone()


include { PANGOLIN } from '../modules/local/pangolin'
include { FILTER_GISAID } from '../modules/local/filter_gisaid' addParams( options: modules['filter_gisaid'] )
include { CONCAT_FASTAS } from '../modules/local/util' addParams( options: modules['concat_fastas'] )
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

  ch_gisaid_sequences = Channel.fromPath(params.gisaid_sequences)
  ch_gisaid_metadata  = Channel.fromPath(params.gisaid_metadata)
  ch_reference_fasta  = Channel.fromPath(params.reference_fasta)
  ch_input            = Channel.fromPath(params.input)

  PANGOLIN(ch_input)
  FILTER_GISAID(
    ch_gisaid_sequences,
    ch_gisaid_metadata,
    PANGOLIN.out.report
  )
  CONCAT_FASTAS(
    FILTER_GISAID.out.fasta.mix(ch_input, ch_reference_fasta).collect()
  )
  NEXTALIGN(
    CONCAT_FASTAS.out,
    ch_reference_fasta
  )
  FILTER_MSA(
    NEXTALIGN.out.fasta,
    PANGOLIN.out.report,
    FILTER_GISAID.out.metadata
  )
  IQTREE(FILTER_MSA.out.fasta)
  PRUNE_TREE(
    IQTREE.out.treefile,
    PANGOLIN.out.report,
    FILTER_MSA.out.metadata
  )
  SEQUENCES_NEXTCLADE(
    PRUNE_TREE.out.metadata,
    CONCAT_FASTAS.out,
    PANGOLIN.out.report
  )
  NEXTCLADE(SEQUENCES_NEXTCLADE.out, 'csv')
  AA_MUTATION_MATRIX(NEXTCLADE.out.csv)
  MERGE_METADATA(
    PRUNE_TREE.out.metadata,
    AA_MUTATION_MATRIX.out,
    PANGOLIN.out.report
  )
  SHIPTV(
    IQTREE.out.treefile,
    PRUNE_TREE.out.leaflist,
    MERGE_METADATA.out
  )
}
