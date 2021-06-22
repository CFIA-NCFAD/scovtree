// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process SHIPTV {
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  conda (params.enable_conda ? "bioconda::shiptv=0.4.1" : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/shiptv:0.4.1--pyh5e36f6f_0'
  } else {
    container 'quay.io/biocontainers/shiptv:0.4.1--pyh5e36f6f_0'
  }

  input:
  path(newick_tree)
  path(leaflist)
  path(metadata)

  output:
  path 'shiptv.html'        , emit: html
  path 'metadata.shiptv.tsv', emit: metadata
  path 'tree.shiptv.newick' , emit: newick
  path '*.version.txt'      , emit: version

  script:
  """
  shiptv \\
    --newick ${newick_tree} \\
    --leaflist $leaflist \\
    --metadata $metadata \\
    --outgroup ${params.reference_name} \\
    --output-html shiptv.html \\
    --output-newick tree.shiptv.newick \\
    --output-metadata-table metadata.shiptv.tsv

  shiptv --version | sed 's/shiptv version //' > shiptv.version.txt
  """
}
