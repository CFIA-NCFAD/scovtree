// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process NEXTALIGN {
  label 'process_high'
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  conda (params.enable_conda ? 'nextalign==0.2.0--h9ee0642_1' : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/nextalign:0.2.0--h9ee0642_1'
  } else {
    container 'quay.io/biocontainers/nextalign:0.2.0--h9ee0642_1'
  }

  input:
  path(sequences)
  path(reference)

  output:
  path "nextalign.*.fasta", emit: fasta
  path "*.version.txt"    , emit: version
  path "nextalign.log"    , emit: log

  script:
  def software = getSoftwareName(task.process)
  """
  nextalign \\
    --sequences=${sequences} \\
    --reference=${reference} \\
    --output-basename=nextalign \\
    2>&1 | tee -a nextalign.log

  nextalign --version > ${software}.version.txt
  """
}
