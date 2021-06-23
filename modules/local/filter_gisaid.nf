// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTER_GISAID {
  label 'process_medium'
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
  path(sequences)
  path(gisaid_sequences)
  path(gisaid_metadata)
  path(lineage_report)

  output:
  path 'gisaid_sequences.filtered.fasta', emit: fasta
  path 'gisaid_metadata.filtered.tsv'   , emit: metadata
  path 'gisaid_metadata.nextstrain.tsv' , emit: nextstrain_metadata
  path 'gisaid_filtering_stats.json'    , emit: stats

  script:  // This script is bundled with the pipeline, in /bin folder
  def region_args = (params.region) ? "--region ${params.region}" : ""
  def country_args = (params.country) ? "--country ${params.country}" : ""
  """
  filter_gisaid.py \\
    $sequences \\
    $gisaid_sequences \\
    $gisaid_metadata \\
    $lineage_report \\
    --min-length ${params.lmin} \\
    --max-length ${params.lmax} \\
    --max-ambig ${params.xambig} \\
    $region_args $country_args \\
    --fasta-output gisaid_sequences.filtered.fasta \\
    --filtered-metadata gisaid_metadata.filtered.tsv \\
    --nextstrain-metadata gisaid_metadata.nextstrain.tsv \\
    --statistics-output gisaid_filtering_stats.json
  """
}
