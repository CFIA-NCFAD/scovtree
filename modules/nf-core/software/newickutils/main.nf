// Import generic module functions
include { initOptions; saveFiles; getSoftwareName} from './functions'

params.options = [:]
options        = initOptions(params.options)

process NW_REROOT {

    label 'process_high'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? 'bioconda newick_utils==1.6--h779adbc_4' : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container 'https://depot.galaxyproject.org/singularity/newick_utils:1.6--h779adbc_4'
    } else {
        container 'quay.io/biocontainers/newick_utils:1.6--h779adbc_4'
    }

    input:
    path (newick_tree)
    path (reference_fasta)

    output:
    path  "*.nwk"               , emit: newick

    script:
    """
    nw_reroot ${newick_tree} `head -1 $reference_fasta | tr -d \">\"` > reroot_phylogenetic_tree.nwk
    """
}