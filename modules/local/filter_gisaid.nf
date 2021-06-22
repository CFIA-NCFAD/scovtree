// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTER_GISAID {
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
  path(gisaid_sequences)
  path(gisaid_metadata)
  path(lineage_report)

  output:
  path 'sequences.filtered.fasta', emit: fasta
  path 'metadata.filtered.tsv'   , emit: metadata
  path 'metadata.nextstrain.tsv' , emit: nextstrain_metadata
  path 'stat.tsv'                , emit: stat

  script:  // This script is bundled with the pipeline, in /bin folder
  """
  filter_gisaid.py \\
    -i $gisaid_sequences \\
    -m $gisaid_metadata \\
    -R $lineage_report \\
    --region '${params.region}' \\
    --country '${params.country}' \\
    -of sequences.filtered.fasta \\
    -fm metadata.filtered.tsv \\
    -nm metadata.nextstrain.tsv \\
    -lmin ${params.lmin} \\
    -lmax ${params.lmax} \\
    -x ${params.xambig} \\
    -ot stat.tsv
  """
}
