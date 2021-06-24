// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTER_MSA {
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  // use shiptv package/container since it has all required Python dependencies
  conda (params.enable_conda ? "bioconda::shiptv=0.4.1" : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/shiptv:0.4.1--pyh5e36f6f_0'
  } else {
    container 'quay.io/biocontainers/shiptv:0.4.1--pyh5e36f6f_0'
  }

  input:
  path(msa)
  path(lineage_report)
  path(metadata)

  output:
  path "msa.filtered.fasta", emit: fasta
  path "metadata.msa.tsv"  , emit: metadata

  script:  // This script is bundled with the pipeline, in /bin folder
  """
  filter_msa.py \\
    --input-fasta $msa \\
    --input-metadata $metadata \\
    --lineage-report $lineage_report \\
    --ref-name ${params.reference_name} \\
    --country ${params.gisaid_focus_country} \\
    --max-seqs ${params.max_msa_seqs} \\
    --output-fasta msa.filtered.fasta \\
    --output-metadata metadata.msa.tsv
  """
}
