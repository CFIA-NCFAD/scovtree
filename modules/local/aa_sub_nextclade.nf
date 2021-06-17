// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process AA_SUBSTITUTION_CHANGE {

    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? "conda-forge::python=3.8.3" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://depot.galaxyproject.org/singularity/mulled-v2-c31f862d526d0a07196020b22083c45f8ddb4f0d:5d34a7705065087f5129c939eea53217c22e38df-0"
    } else {
        container "quay.io/biocontainers/mulled-v2-c31f862d526d0a07196020b22083c45f8ddb4f0d:5d34a7705065087f5129c939eea53217c22e38df-0"
    }

    input:
    path (metadata)

    output:
    path "*.tsv", optional:true, emit: tsv

    script:  // This script is bundled with the pipeline, in /bin folder
    aa_substitution_change = "aa_substitution_change.tsv"
    """
    aa_sub_nextclade.py -m $metadata -o $aa_substitution_change
    """
}