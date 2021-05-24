// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process IQTREE_PHYLOGENETICTREE {

    label 'process_high'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? 'bioconda::iqtree=2.1.2' : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container 'https://depot.galaxyproject.org/singularity/iqtree:2.1.2--h56fc30b_0'
    } else {
        container 'quay.io/biocontainers/iqtree:2.1.2--h56fc30b_0'
    }

    input:
    path (msa_mafft)

    output:
    path "*.iqtree"                , emit: report
    path "*.treefile"              , emit: treefile
    path "*.mldist"                , emit: distance
    path "*.log"                   , emit: log
    path "*.version.txt"           , emit: version

    script:
    def software = getSoftwareName(task.process)
    """
    iqtree \\
        -s ${msa_mafft} \\
        -redo \\
        -o ${params.reference_name} \\
        -T ${task.cpus} \\
        -ninit 2 \\
        -n 5 \\
        -me 1.0 \\
        -experimental \\
        -t NJ-R \\
        --no-opt-gamma-inv \\
        -m ${params.substitution_model}\\
        --prefix iqtree-MN908947.3-GTR
    iqtree --version | sed "s/iqtree //g" > ${software}.version.txt
    """
}