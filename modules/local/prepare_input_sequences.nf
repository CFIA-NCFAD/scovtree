// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process PREPARE_INPUT_SEQUENCES {
  label 'process_low'
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
  path(fasta)

  output:
  path 'input_sequences.correctedID.fasta' , emit: fasta

  script:
  """
  prepare_input_sequences.py \\
      $fasta \\
      --fasta-output input_sequences.correctedID.fasta
  """
}
