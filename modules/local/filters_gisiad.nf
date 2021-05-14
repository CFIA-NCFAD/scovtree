// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process FILTERS_GISIAD {

    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? "conda-forge::python=3.8.3" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://depot.galaxyproject.org/singularity/mulled-v2-480c331443a1d7f4cb82aa41315ac8ea4c9c0b45:3e0fc1ebdf2007459f18c33c65d38d2b031b0052-0"
    } else {
        container "quay.io/biocontainers/mulled-v2-480c331443a1d7f4cb82aa41315ac8ea4c9c0b45:3e0fc1ebdf2007459f18c33c65d38d2b031b0052-0"
    }

    input:
    path (gisaid_sequences)
    path (gisaid_metadata)

    output:
    path "*.fasta"       , emit: gisiad_fasta
    path "*.tsv"         , emit: gisiad_metadata

    script:  // This script is bundled with the pipeline, in /bin folder
    filtered_fasta_output     = "filtered_gisiad_sequences.fasta"
    filtered_metadata_output1 = "metadata_1.tsv"
    filtered_metadata_output2 = "metadata_2.tsv"
    """
    filter_gisaid_sequences.py -i $gisaid_sequences -m $gisaid_metadata \\
                               -s '${params.sample_lineage}' -r '${params.region}' -c '${params.country}' \\
                               -of $filtered_fasta_output -om1 $filtered_metadata_output1 -om2 $filtered_metadata_output2 \\
                               -lmin ${params.lmin} -lmax ${params.lmax} -x ${params.xambig}
    """
}