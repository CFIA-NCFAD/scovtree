// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process PHYLOGENETICTREE_SNPS {

    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    conda (params.enable_conda ? "conda-forge::r-base=4.0.3 conda-forge::r-optparse=1.6.6 conda-forge::r-tidyr=1.1.0 conda-forge::r-tidyverse=1.3.0 conda-forge::r-ggplot2=3.3.3 conda-forge::r-phangorn=2.6.3 conda-forge::r-readr=1.4.0 bioconda::bioconductor-ggtree=2.4.1 bioconda::bioconductor-treeio=1.14.3" : null)
    if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
        container "https://depot.galaxyproject.org/singularity/bioconductor-ggtree:2.4.1--r40hdfd78af_0"
    } else {
        container "quay.io/biocontainers/bioconductor-ggtree:2.4.1--r40hdfd78af_0"
    }

    input:
    path (newick)
    path (alleles)
    path (lineage_report)

    output:
    path "*.pdf"  , emit : visualization_tree

    script:  // This script is bundled with the pipeline, in /bin folder
    """
    phylogenetic_tree_snps.r phylogentic_tree_snps.pdf ${newick} ${alleles} ${lineage_report}
    """
}