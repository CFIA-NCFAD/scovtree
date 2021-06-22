// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process ALIGN2ALLELES {
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? "conda-forge::python=3.8.3 bioconda::pysam" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://depot.galaxyproject.org/singularity/mulled-v2-480c331443a1d7f4cb82aa41315ac8ea4c9c0b45:3e0fc1ebdf2007459f18c33c65d38d2b031b0052-0"
    } else {
        container "quay.io/biocontainers/mulled-v2-480c331443a1d7f4cb82aa41315ac8ea4c9c0b45:3e0fc1ebdf2007459f18c33c65d38d2b031b0052-0"
    }

    input:
    path (fasta)

    output:
    path "alleles.tsv"

    script:  // This script is bundled with the pipeline, in /bin folder
    """
    align2alleles.py \\
        --reference-name ${params.reference_name} \\
        ${fasta} > alleles.tsv
    """
}
