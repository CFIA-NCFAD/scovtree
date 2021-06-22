// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process PANGOLIN {
  label 'process_medium'
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  conda (params.enable_conda ? 'bioconda::pangolin=3.1.3' : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/pangolin:3.1.3--pyhdfd78af_0'
  } else {
    container 'quay.io/biocontainers/pangolin:3.1.3--pyhdfd78af_0'
  }

  input:
  path(fasta)

  output:
  path 'pangolin.csv' , emit: report
  path '*.version.txt', emit: version

  script:
  def software = getSoftwareName(task.process)
  """
  pangolin \\
      $fasta \\
      --outfile pangolin.csv \\
      --threads $task.cpus

  pangolin --version | sed "s/pangolin //g" > ${software}.version.txt
  """
}
