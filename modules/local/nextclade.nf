// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process NEXTCLADE {
    label 'process_high_cpu_medium_mem'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

    conda (params.enable_conda ? "bioconda::nextclade_js=0.14.4" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
      container 'https://depot.galaxyproject.org/singularity/nextclade_js:0.14.4--h9ee0642_0'
    } else {
      container 'quay.io/biocontainers/nextclade_js:0.14.4--h9ee0642_0'
    }


    input:
    path(fasta)
    val output_format

    output:
    path("nextclade.csv")      , optional:true, emit: csv
    path("nextclade.json")      , optional:true, emit: json
    path("nextclade.tree.json") , optional:true, emit: json_tree
    path("nextclade.tsv")       , optional:true, emit: tsv
    path("nextclade.clades.tsv"), optional:true, emit: tsv_clades
    path "*.version.txt"                         , emit: version

    script:
    def software = getSoftwareName(task.process)
    def format   = output_format
    if (!(format in ['json', 'csv', 'tsv', 'tree', 'tsv-clades-only'])) {
        format = 'json'
    }
    def extension = format
    if (format in ['tsv-clades-only']) {
        extension = '.clades.tsv'
    } else if (format in ['tree']) {
        extension = 'tree.json'
    }
    """
    nextclade \\
        $options.args \\
        --jobs $task.cpus \\
        --input-fasta $fasta \\
        --output-${format} nextclade.${extension}

    echo \$(nextclade --version 2>&1) > ${software}.version.txt
    """
}
