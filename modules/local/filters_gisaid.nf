// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTERS_GISAID {

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
    path (gisaid_sequences)
    path (gisaid_metadata)
    path (lineage_report)

    output:
    path "*.fasta"         , emit: fasta
    path "*_1.tsv"         , emit: metadata_1
    path "*_2.tsv"         , emit: metadata_2
    path "*t.tsv"          , emit: stat

    script:  // This script is bundled with the pipeline, in /bin folder
    filtered_fasta_output     = "filtered_gisaid_sequences.fasta"
    filtered_metadata_output1 = "metadata_1.tsv"
    filtered_metadata_output2 = "metadata_2.tsv"
    statistics_output         = "stat.tsv"
    """
    filter_gisaid_sequences.py -i $gisaid_sequences -m $gisaid_metadata \\
                               -s '${params.sample_lineage}' -R $lineage_report -r '${params.region}' -c '${params.country}' \\
                               -of $filtered_fasta_output -om1 $filtered_metadata_output1 -om2 $filtered_metadata_output2 \\
                               -lmin ${params.lmin} -lmax ${params.lmax} -x ${params.xambig} -ot $statistics_output
    """
}