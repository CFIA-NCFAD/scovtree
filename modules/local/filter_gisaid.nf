// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTER_GISAID {
  label 'process_high_mem'
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
  path 'filter_gisaid.py.log'           , emit: log

  script:  // This script is bundled with the pipeline, in /bin folder
  def region_args = (params.gisaid_region) ? "--region \"${params.gisaid_region}\"" : ""
  def country_args = (params.gisaid_country) ? "--country \"${params.gisaid_country}\"" : ""
  def date_start = (params.gisaid_date_start) ? "--date-start ${params.gisaid_date_start}" : ""
  def date_end = (params.gisaid_date_end) ? "--date-end ${params.gisaid_date_end}" : ""
  def pangolin_lineages = (params.gisaid_pangolin_lineages) ? "--pangolin-lineages ${params.gisaid_pangolin_lineages}" : ""
  """
  filter_gisaid.py \\
    $sequences \\
    $gisaid_sequences \\
    $gisaid_metadata \\
    $lineage_report \\
    --min-length ${params.gisaid_min_length} \\
    --max-length ${params.gisaid_max_length} \\
    --max-ambig ${params.gisaid_max_ambig} \\
    --max-gisaid-seqs ${params.max_gisaid_filtered_seqs} \\
    $region_args $country_args $date_start $date_end $pangolin_lineages \\
    --fasta-output gisaid_sequences.filtered.fasta \\
    --filtered-metadata gisaid_metadata.filtered.tsv \\
    --nextstrain-metadata gisaid_metadata.nextstrain.tsv \\
    --statistics-output gisaid_filtering_stats.json \\
    2>&1 | tee -a filter_gisaid.py.log
  """
}
