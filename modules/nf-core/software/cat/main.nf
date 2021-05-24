
process CAT_SEQUENCES {

    label 'process_low'

    conda (params.enable_conda ? "conda-forge::sed=4.7" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://containers.biocontainers.pro/s3/SingImgsRepo/biocontainers/v1.2.0_cv1/biocontainers_v1.2.0_cv1.img"
    } else {
        container "biocontainers/biocontainers:v1.2.0_cv1"
    }

    input:
    path (filter_gisiad_sequences)
    path (input_sequences)

    output:
    path("*.fasta"), emit: merged_sequences

    script:

    """
    cat ${params.reference_fasta} ${filter_gisiad_sequences} ${input_sequences} > merged_sequences.fasta
    """
}
