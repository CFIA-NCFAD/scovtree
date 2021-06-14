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
    path (metadata)

    output:
    path "*.tsv"         , emit: metadata

    script:  // This script is bundled with the pipeline, in /bin folder
    filtered_shiptv_metadata   = "shiptv_filtered_metadata.tsv"
    """
    filter_column_shiptv.py -M $metadata -m $filtered_shiptv_metadata \\
                            --skip-virus-name=${params.skip_virus_name}\\
                            --skip-type=${params.skip_type} \\
                            --skip-accession-id=${params.skip_virus_name} \\
                            --skip-collection-date=${params.skip_accession_id} \\
                            --skip-location=${params.skip_location} \\
                            --skip-additional-location-information=${params.skip_additional_location_information} \\
                            --skip-sequence-length=${params.skip_sequence_length} \\
                            --skip-host=${params.skip_host} \\
                            --skip-patient-age=${params.skip_patient_age} \\
                            --skip-gender=${params.skip_gender} \\
                            --skip-clade=${params.skip_clade} \\
                            --skip-pango-lineage=${params.skip_pango_lineage} \\
                            --skip-pangolin-version=${params.skip_pangolin_version} \\
                            --skip-variant=${params.skip_variant} \\
                            --skip-aa-substitutions=${params.skip_aa_substitutions} \\
                            --skip-submission-date=${params.skip_submission_date} \\
                            --skip-is-reference=${params.skip_is_reference} \\
                            --skip-is-complete=${params.skip_is_complete} \\
                            --skip-is-high-coverage=${params.skip_is_high_coverage} \\
                            --skip-is-low-coverage=${params.skip_is_low_coverage} \\
                            --skip-n-content=${params.skip_n_content} \\
                            --skip-gc-content=${params.skip_gc_content}
    """
}