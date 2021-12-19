// Import generic module functions
include { initOptions; saveFiles; getSoftwareName } from './functions'

params.options = [:]
options        = initOptions(params.options)

process PRUNE_TREE {
  // default process reqs sufficient
  publishDir "${params.outdir}",
      mode: params.publish_dir_mode,
      saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:[:], publish_by_meta:[]) }

  // use shiptv package/container since it has all required Python dependencies
  conda (params.enable_conda ? "bioconda::shiptv=0.4.1" : null)
  if (workflow.containerEngine == 'singularity' && !params.singularity_pull_docker_container) {
    container 'https://depot.galaxyproject.org/singularity/shiptv:0.4.1--pyh5e36f6f_0'
  } else {
    container 'quay.io/biocontainers/shiptv:0.4.1--pyh5e36f6f_0'
  }

  input:
  path (newick)
  path (pangolin_report)
  path (metadata)

  output:
  path "leaflist"             , emit: leaflist
  path "metadata.leaflist.tsv", emit: metadata

  script:  // This script is bundled with the pipeline, in /bin folder
  """
  prune_tree.py \\
    $newick \\
    $metadata \\
    $pangolin_report \\
    --ref-name ${params.reference_name} \\
    --leaflist leaflist \\
    --metadata-output metadata.leaflist.tsv \\
    --max-taxa ${params.max_taxa}
  """
}
