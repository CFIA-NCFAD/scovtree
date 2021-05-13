// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process MAFFT_MSA {

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
    path (consensus_sequences)
    path (reference_fasta)

    output:
    path  "*.fasta"               , emit: fasta
    path  "*.version.txt"         , emit: version

    script:
    def software = getSoftwareName(task.process)
    """
    mafft \\
        $options.args \\
        --thread ${task.cpus} \\
        --addfragments ${consensus_sequences}\\
        $reference_fasta > sequences_alignment.fasta
    mafft --version | sed "s/mafft //g" > ${software}.version.txt
    """
}