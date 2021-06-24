// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process MAFFT {

    label 'process_high'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? 'bioconda::mafft=7.475' : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container 'https://depot.galaxyproject.org/singularity/mafft:7.475--h779adbc_1'
    } else {
        container 'quay.io/biocontainers/mafft:7.475--h779adbc_1'
    }

    input:
    path(sequences)
    path(reference_fasta)

    output:
    path "sequences.mafft.fasta", emit: fasta
    path "*.version.txt"        , emit: version

    script:
    def software = getSoftwareName(task.process)
    """
    mafft \\
        $options.args \\
        --thread ${task.cpus} \\
        --addfragments ${sequences}\\
        $reference_fasta > sequences.mafft.fasta
    (mafft --version 2>&1) | sed -E 's/^v(\\S+).*/\\1/' > ${software}.version.txt
    """
}
