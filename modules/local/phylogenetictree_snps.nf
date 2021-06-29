// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process PHYLOGENETICTREE_SNPS {
    label 'process_low'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

    conda (params.enable_conda ? "bioconda::bioconductor-ggtree=3.0.1" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
      container 'https://depot.galaxyproject.org/singularity/bioconductor-ggtree:3.0.1--r41hdfd78af_0'
    } else {
      container 'quay.io/biocontainers/bioconductor-ggtree:3.0.1--r41hdfd78af_0'
    }


    input:
    path (newick)
    path (alleles)
    path (lineage_report)

    output:
    path "phylogentic_tree_snps.pdf"

    script:  // This script is bundled with the pipeline, in /bin folder
    """
    phylogenetic_tree_snps.r phylogentic_tree_snps.pdf ${newick} ${alleles} ${lineage_report}
    """
}
