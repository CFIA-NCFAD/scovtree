// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTERS_SHIPTV_METADATA {

    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? "conda-forge::python bioconda::pysam conda-forge::biopython conda-forge::click conda-forge::pandas conda-forge::numpy conda-forge::ete3" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://depot.galaxyproject.org/singularity/mulled-v2-c31f862d526d0a07196020b22083c45f8ddb4f0d:5d34a7705065087f5129c939eea53217c22e38df-0"
    } else {
        container "quay.io/biocontainers/mulled-v2-c31f862d526d0a07196020b22083c45f8ddb4f0d:5d34a7705065087f5129c939eea53217c22e38df-0"
    }

    input:
    path (gisiad_metadata)
    path (aachange_metadata)
    path (pangolin_report)

    output:
    path "*.tsv"         , emit: metadata

    script:  // This script is bundled with the pipeline, in /bin folder
    filtered_shiptv_metadata   = "shiptv_filtered_metadata.tsv"
    """
    filter_column_shiptv.py -M $gisiad_metadata -m $filtered_shiptv_metadata -ma $aachange_metadata -p $pangolin_report \\
                            -d ${params.drop_gisaid_columns} \\
                            --skip-aa-substitution-change=${params.skip_aa_substitution_change}
    """
}