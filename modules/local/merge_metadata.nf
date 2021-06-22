// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process MERGE_METADATA{
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
  path(gisaid_metadata)
  path(aa_mutation_matrix)
  path(pangolin_report)

  output:
  path "metadata.merged.tsv"

  script:  // This script is bundled with the pipeline, in /bin folder
  def aa_mutation_matrix_opt = (aa_mutation_matrix) ? "--aa-mutation-matrix $aa_mutation_matrix" : ""
  def select_metadata_fields = (params.visualize_gisaid_metadata) ? "--select-metadata-fields \"${params.visualize_gisaid_metadata}\"" : ""
  """
  merge_metadata.py \\
    $gisaid_metadata \\
    $pangolin_report \\
    $aa_mutation_matrix_opt $select_metadata_fields \\
    --metadata-output metadata.merged.tsv
  """
}
