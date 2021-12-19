// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process IQTREE {
  label 'process_high'
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  conda (params.enable_conda ? 'bioconda::iqtree=2.1.4_beta' : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/iqtree:2.1.4_beta--hdcc8f71_0'
  } else {
    container 'quay.io/biocontainers/iqtree:2.1.4_beta--hdcc8f71_0'
  }

  input:
  path(msa)

  output:
  path 'iqtree-*.iqtree'  , emit: report
  path 'iqtree-*.treefile', emit: treefile
  path 'iqtree-*.mldist'  , emit: distance
  path 'iqtree-*.log'     , emit: log
  path '*.version.txt'    , emit: version

  script:
  def software = getSoftwareName(task.process)
  """
  iqtree \\
      $options.args \\
      -s ${msa} \\
      -o ${params.reference_name} \\
      -T ${task.cpus} \\
      -m ${params.substitution_model} \\
      --prefix iqtree-${params.reference_name}-${params.substitution_model}

  (iqtree --version 2>&1) | head -n1 | sed -E 's/^IQ-TREE multicore version (\\S+) .*/\\1/' > ${software}.version.txt
  """
}
