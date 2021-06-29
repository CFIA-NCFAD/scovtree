// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)
// TODO: use merge_metadata.nf instead of having 2 processes that perform similar tasks (PK, 2021-06-28)
process SHIPTV_METADATA {
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  conda (params.enable_conda ? "bioconda::shiptv=0.4.1" : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/shiptv:0.4.1--pyh5e36f6f_0'
  } else {
    container 'quay.io/biocontainers/shiptv:0.4.1--pyh5e36f6f_0'
  }

  input:
  path(newick)
  path(aa_mutation_matrix)
  path(lineage_report)

  output:
  path "leaflist"           , emit: leaflist
  path "metadata.merged.tsv", emit: metadata

  script:  // This script is bundled with the pipeline, in /bin folder
  def aa_mutation_matrix_opt = (aa_mutation_matrix) ? "--aa-mutation-matrix $aa_mutation_matrix" : ""
  """
  shiptv_metadata.py \\
    $newick \\
    $lineage_report \\
    $aa_mutation_matrix_opt \\
    --leaflist leaflist \\
    --metadata-output metadata.merged.tsv
  """
}
