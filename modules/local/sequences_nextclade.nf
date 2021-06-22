// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process SEQUENCES_NEXTCLADE {
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
  path(metadata)
  path(sequences)
  path(pangolin_report)

  output:
  path "sequences.nextclade.fasta"

  script:  // This script is bundled with the pipeline, in /bin folder
  """
  sequences_nextclade.py \\
    $sequences \\
    $metadata \\
    $pangolin_report \\
    --output-sequences sequences.nextclade.fasta \\
    --ref-name ${params.reference_name}
  """
}
