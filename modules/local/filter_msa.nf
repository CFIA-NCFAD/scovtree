// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTERS_MSA {

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
    path (msa)
    path (lineage_report)
    path (metadata)

    output:
    path "*.fasta"       , emit: fasta
    path "*.tsv"         , emit: metadata

    script:  // This script is bundled with the pipeline, in /bin folder
    filtered_msa_fasta      = "filtered_msa_sequences.fasta"
    filtered_msa_metadata   = "filtered_msa_metadata.tsv"
    """
    filter_msa_align.py -i $msa -M $metadata -r $lineage_report -t ${params.msa_threshold_filter} -o $filtered_msa_fasta -m $filtered_msa_metadata
    """
}