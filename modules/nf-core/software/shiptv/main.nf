// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process SHIPTV_VISUALIZATION {

    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? "shiptv==0.4.0--pyh5e36f6f_0" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://depot.galaxyproject.org/singularity/shiptv:0.4.0--pyh5e36f6f_0"
    } else {
        container "quay.io/biocontainers/shiptv:0.4.0--pyh5e36f6f_0"
    }

    input:
    path (newick_tree)

    output:
    path  "*.html"               , emit: visualization_html
    path  "*.tsv"                , emit: metadata_tsv

    script:
    """
    shiptv -n ${newick_tree} -o shiptv_phylogenetic_tree.html -m shiptv_metadata.tsv
    """
}