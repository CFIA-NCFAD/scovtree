
process CAT_SEQUENCES {

    label 'process_low'

    conda (params.enable_conda ? "conda-forge::sed=4.7" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://containers.biocontainers.pro/s3/SingImgsRepo/biocontainers/v1.2.0_cv1/biocontainers_v1.2.0_cv1.img"
    } else {
        container "biocontainers/biocontainers:v1.2.0_cv1"
    }

    input:
    path (filter_gisaid_sequences)
    path (input_sequences)
    path (ref_sequence)

    output:
    path("*.fasta"), emit: merged_sequences

    script:

    """
    cat ${ref_sequence} ${filter_gisaid_sequences} ${input_sequences} > merged_sequences.fasta
    """
}
