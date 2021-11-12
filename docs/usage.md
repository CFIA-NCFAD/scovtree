# CFIA-NCFAD/scovtree: Usage

## Introduction

## Running the pipeline

The pipeline has 2 workflows:

* Phylogenetic analysis with input SARS-CoV-2 sequences

  ```bash
  nextflow run CFIA-NCFAD/scovtree \
    -profile docker \
    --input your-sars-cov-2-sequences.fasta
  ```

* Phylogenetic analysis with input SARS-CoV-2 sequences and related GISAID sequences

  ```bash
  nextflow run CFIA-NCFAD/scovtree \
    -profile docker \
    --input your-sars-cov-2-sequences.fasta \
    --gisaid_sequences sequences_fasta_2021_06_14.tar.xz \
    --gisaid_metadata metadata_tsv_2021_06_14.tar.xz
  ```

  > Both `--gisaid_sequences` and `--gisaid_metadata` need to be specified to produce a phylogenetic tree of your sequences and closely related GISAID sequences.

This will launch the pipeline with the `docker` configuration profile. See below for more information about profiles.

Note that the pipeline will create the following files in your working directory:

```bash
work            # Directory containing the nextflow working files
results         # Finished results (configurable, see below)
.nextflow_log   # Log file from Nextflow
# Other nextflow hidden files, eg. history of pipeline runs and old logs.
```

### Input/Output options

Define where the pipeline should find input data and save output data.

#### `--input`

* Optional
* Type: string

Path to FASTA file with SARS-CoV-2 sequences.

#### `--outdir`

* Optional
* Type: string
* Default: `./results`

The output directory where the results will be saved.

#### `--reference_name`

* Optional
* Type: string
* Default: `MN908947.3`

Name of reference sequence.

#### `--reference_fasta`

* Optional
* Type: string
* Default: `https://raw.githubusercontent.com/CFIA-NCFAD/nf-test-datasets/scovtree/nCoV-2019.reference.fasta`

Reference SARS-CoV-2 genome sequence FASTA file.

#### `--gisaid_sequences`

* Optional
* Type: string

Path to GISAID SARS-CoV-2 sequences (e.g. `sequences_fasta_2021_08_03.tar.xz`)

#### `--gisaid_metadata`

* Optional
* Type: string

Path to GISAID SARS-CoV-2 metadata (e.g. `metadata_tsv_2021_08_03.tar.xz`)

### GISAID Sequence Filtering Options

Options for filtering GISAID sequences based on sequence quality and metadata.

#### `--gisaid_country`

* Optional
* Type: string

Select GISAID sequences from a particular country.

#### `--gisaid_region`

* Optional
* Type: string

Select GISAID sequences from a particular geographical region.

#### `--gisaid_min_length`

* Optional
* Type: integer
* Default: `28000`

Remove GISAID sequences shorter than this value.

#### `--gisaid_max_length`

* Optional
* Type: integer
* Default: `31000`

Remove GISAID sequences longer than this value.

#### `--gisaid_max_ambig`

* Optional
* Type: integer
* Default: `3000`

Remove GISAID sequences with more than this number of ambiguous sites (non 'A', 'C', 'G' or 'T' sites).

#### `--gisaid_focus_country`

* Optional
* Type: string
* Default: `Canada`

Ensure that GISAID sequences from this country and belonging to the same Pangolin lineage as your input sequences are represented in the tree.

#### `--max_gisaid_filtered_seqs`

* Optional
* Type: integer
* Default: `100000`

Max number of GISAID sequences to filter initially. Set lower to reduce computational burden especially for large lineages (e.g. B.1.1.7).

### IQ-TREE Options

IQ-TREE phylogenetic tree creation options

#### `--substitution_model`

* Optional
* Type: string
* Default: `GTR`

Substitution model

#### `--max_msa_seqs`

* Optional
* Type: integer
* Default: `10000`

Max number of multiple sequence alignment (MSA) sequences for phylogenetic analysis

### Shiptv visualization Options

Define where metadata columns will be kept for visualization

#### `--max_taxa`

* Optional
* Type: integer
* Default: `75`

Maximum taxa to show in shiptv tree including your input sequences so that the relationships between your sequences and closely related public sequences are easier to see and focus on.

#### `--select_gisaid_metadata`

* Optional
* Type: string

Specify which GISAID metadata fields to show in shiptv tree. Only these fields will be shown. If not specified, all fields will be shown.

> **NOTE:** e.g. `--select_gisaid_metadata 'Type,Location,Clade,Variant,AA_Substitutions,Collection_date'`

### Process skipping options

Options to skip certain non-essential processes.

#### `--skip_nextclade`

* Optional
* Type: boolean

Skip running Nextclade. No amino acid mutation matrix will be produced and merged with other sequence metadata and shown in the shiptv tree.

#### `--skip_snp_tree`

* Optional
* Type: boolean

Skip generating R ggtree phylogenetic tree PDF with SNPs visualized beside the tree.

### Generic options

Less common options for the pipeline, typically set in a config file.

#### `--help`

* Optional
* Type: boolean

Display help text.

#### `--publish_dir_mode`

* Optional
* Type: string
* Default: `copy`

Method used to save pipeline results to output directory.

> **NOTE:** The Nextflow `publishDir` option specifies which intermediate files should be saved to the output directory. This option tells the pipeline what method should be used to move these files. See [Nextflow docs](https://www.nextflow.io/docs/latest/process.html#publishdir) for details.

#### `--validate_params`

* Optional
* Type: boolean
* Default: `True`

Boolean whether to validate parameters against the schema at runtime

#### `--email_on_fail`

* Optional
* Type: string

Email address for completion summary, only when pipeline fails.

> **NOTE:** This works exactly as with `--email`, except emails are only sent if the workflow is not successful.

#### `--plaintext_email`

* Optional
* Type: boolean

Send plain-text email instead of HTML.

> **NOTE:** Set to receive plain-text e-mails instead of HTML formatted.

#### `--max_multiqc_email_size`

* Optional
* Type: string
* Default: `25.MB`

File size limit when attaching MultiQC reports to summary emails.

> **NOTE:** If file generated by pipeline exceeds the threshold, it will not be attached.

#### `--monochrome_logs`

* Optional
* Type: boolean

Do not use coloured log outputs.

> **NOTE:** Set to disable colourful command line output and live life in monochrome.

#### `--multiqc_config`

* Optional
* Type: string

Custom config file to supply to MultiQC.

#### `--tracedir`

* Optional
* Type: string
* Default: `${params.outdir}/pipeline_info`

Directory to keep pipeline Nextflow logs and reports.

#### `--enable_conda`

* Optional
* Type: boolean

Run this workflow with Conda. You can also use '-profile conda' instead of providing this parameter.

#### `--singularity_pull_docker_container`

* Optional
* Type: boolean

Instead of directly downloading Singularity images for use with Singularity, force the workflow to pull and convert Docker containers instead.

> **NOTE:** This may be useful for example if you are unable to directly pull Singularity containers to run the pipeline due to http/https proxy issues.

#### `--show_hidden_params`

* Optional
* Type: boolean

Show all params when using `--help`

> **NOTE:** By default, parameters set as _hidden_ in the schema are not shown on the command line when a user runs with `--help`. Specifying this option will tell the pipeline to show all parameters.

### Max job request options

Set the top limit for requested resources for any single job.

#### `--max_cpus`

* Optional
* Type: integer
* Default: `16`

Maximum number of CPUs that can be requested    for any single job.

> **NOTE:** Use to set an upper-limit for the CPU requirement for each process. Should be an integer e.g. `--max_cpus 1`

#### `--max_memory`

* Optional
* Type: string
* Default: `128.GB`

Maximum amount of memory that can be requested for any single job.

> **NOTE:** Use to set an upper-limit for the memory requirement for each process. Should be a string in the format integer-unit e.g. `--max_memory '8.GB'`

#### `--max_time`

* Optional
* Type: string
* Default: `240.h`

Maximum amount of time that can be requested for any single job.

> **NOTE:** Use to set an upper-limit for the time requirement for each process. Should be a string in the format integer-unit e.g. `--max_time '2.h'`

### Institutional config options

Parameters used to describe centralised config profiles. These should not be edited.

#### `--custom_config_version`

* Optional
* Type: string
* Default: `master`

Git commit id for Institutional configs.

> **NOTE:** Provide git commit id for custom Institutional configs hosted at `nf-core/configs`. This was implemented for reproducibility purposes. Default: `master`.

```bash
## Download and use config file with following git commit id
--custom_config_version d52db660777c4bf36546ddb188ec530c3ada1b96
```

#### `--custom_config_base`

* Optional
* Type: string
* Default: `https://raw.githubusercontent.com/nf-core/configs/master`

Base directory for Institutional configs.

> **NOTE:** If you're running offline, nextflow will not be able to fetch the institutional config files from the internet. If you don't need them, then this is not a problem. If you do need them, you should download the files from the repo and tell nextflow where to find them with the `custom_config_base` option. For example:

```bash
## Download and unzip the config files
cd /path/to/my/configs
wget https://github.com/nf-core/configs/archive/master.zip
unzip master.zip

## Run the pipeline
cd /path/to/my/data
nextflow run /path/to/pipeline/ --custom_config_base /path/to/my/configs/configs-master/
```

> Note that the nf-core/tools helper package has a `download` command to download all required pipeline files + singularity containers + institutional configs in one go for you, to make this process easier.

#### `--hostnames`

* Optional
* Type: string

Institutional configs hostname.

#### `--config_profile_name`

* Optional
* Type: string

Institutional config name.

#### `--config_profile_description`

* Optional
* Type: string

Institutional config description.

#### `--config_profile_contact`

* Optional
* Type: string

Institutional config contact information.

#### `--config_profile_url`

* Optional
* Type: string

Institutional config URL link.

### Updating the pipeline

When you run the above command, Nextflow automatically pulls the pipeline code from GitHub and stores it as a cached version. When running the pipeline after this, it will always use the cached version if available - even if the pipeline has been updated since. To make sure that you're running the latest version of the pipeline, make sure that you regularly update the cached version of the pipeline:

```bash
nextflow pull CFIA-NCFAD/scovtree
```

### Reproducibility

It's a good idea to specify a pipeline version when running the pipeline on your data. This ensures that a specific version of the pipeline code and software are used when you run your pipeline. If you keep using the same tag, you'll be running the same version of the pipeline, even if there have been changes to the code since.

First, go to the [CFIA-NCFAD/scovtree releases page](https://github.com/CFIA-NCFAD/scovtree/releases) and find the latest version number - numeric only (eg. `1.3.1`). Then specify this when running the pipeline with `-r` (one hyphen) - eg. `-r 1.5.0`.

This version number will be logged in reports when you run the pipeline, so that you'll know what you used when you look back in the future.

## Core Nextflow arguments

> **NB:** These options are part of Nextflow and use a _single_ hyphen (pipeline parameters use a double-hyphen).

### `-profile`

Use this parameter to choose a configuration profile. Profiles can give configuration presets for different compute environments.

Several generic profiles are bundled with the pipeline which instruct the pipeline to use software packaged using different methods (Docker, Singularity, Podman, Shifter, Charliecloud, Conda) - see below.

> We highly recommend the use of Docker or Singularity containers for full pipeline reproducibility, however when this is not possible, Conda is also supported.

The pipeline also dynamically loads configurations from [https://github.com/nf-core/configs](https://github.com/nf-core/configs) when it runs, making multiple config profiles for various institutional clusters available at run time. For more information and to see if your system is available in these configs please see the [nf-core/configs documentation](https://github.com/nf-core/configs#documentation).

Note that multiple profiles can be loaded, for example: `-profile test,docker` - the order of arguments is important!
They are loaded in sequence, so later profiles can overwrite earlier profiles.

If `-profile` is not specified, the pipeline will run locally and expect all software to be installed and available on the `PATH`. This is _not_ recommended.

* `docker`
  * A generic configuration profile to be used with [Docker](https://docker.com/)
  * Pulls software from Docker Hub: [`nfcore/scovtree`](https://hub.docker.com/r/nfcore/scovtree/)
* `singularity`
  * A generic configuration profile to be used with [Singularity](https://sylabs.io/docs/)
  * Pulls software from Docker Hub: [`nfcore/scovtree`](https://hub.docker.com/r/nfcore/scovtree/)
* `podman`
  * A generic configuration profile to be used with [Podman](https://podman.io/)
  * Pulls software from Docker Hub: [`nfcore/scovtree`](https://hub.docker.com/r/nfcore/scovtree/)
* `shifter`
  * A generic configuration profile to be used with [Shifter](https://nersc.gitlab.io/development/shifter/how-to-use/)
  * Pulls software from Docker Hub: [`nfcore/scovtree`](https://hub.docker.com/r/nfcore/scovtree/)
* `charliecloud`
  * A generic configuration profile to be used with [Charliecloud](https://hpc.github.io/charliecloud/)
  * Pulls software from Docker Hub: [`nfcore/scovtree`](https://hub.docker.com/r/nfcore/scovtree/)
* `conda`
  * Please only use Conda as a last resort i.e. when it's not possible to run the pipeline with Docker, Singularity, Podman, Shifter or Charliecloud.
  * A generic configuration profile to be used with [Conda](https://conda.io/docs/)
  * Pulls most software from [Bioconda](https://bioconda.github.io/)
* `test`
  * A profile with a complete configuration for automated testing
  * Includes links to test data so needs no other parameters

### `-resume`

Specify this when restarting a pipeline. Nextflow will used cached results from any pipeline steps where the inputs are the same, continuing from where it got to previously.

You can also supply a run name to resume a specific run: `-resume [run-name]`. Use the `nextflow log` command to show previous run names.

### `-c`

Specify the path to a specific config file (this is a core Nextflow command). See the [nf-core website documentation](https://nf-co.re/usage/configuration) for more information.

#### Custom resource requests

Each step in the pipeline has a default set of requirements for number of CPUs, memory and time. For most of the steps in the pipeline, if the job exits with an error code of `143` (exceeded requested resources) it will automatically resubmit with higher requests (2 x original, then 3 x original). If it still fails after three times then the pipeline is stopped.

Whilst these default requirements will hopefully work for most people with most data, you may find that you want to customise the compute resources that the pipeline requests. You can do this by creating a custom config file. For example, to give the workflow process `star` 32GB of memory, you could use the following config:

```nextflow
process {
  withName: star {
    memory = 32.GB
  }
}
```

To find the exact name of a process you wish to modify the compute resources, check the live-status of a nextflow run displayed on your terminal or check the nextflow error for a line like so: `Error executing process > 'bwa'`. In this case the name to specify in the custom config file is `bwa`.

See the main [Nextflow documentation](https://www.nextflow.io/docs/latest/config.html) for more information.

If you are likely to be running `nf-core` pipelines regularly it may be a good idea to request that your custom config file is uploaded to the `nf-core/configs` git repository. Before you do this please can you test that the config file works with your pipeline of choice using the `-c` parameter (see definition above). You can then create a pull request to the `nf-core/configs` repository with the addition of your config file, associated documentation file (see examples in [`nf-core/configs/docs`](https://github.com/nf-core/configs/tree/master/docs)), and amending [`nfcore_custom.config`](https://github.com/nf-core/configs/blob/master/nfcore_custom.config) to include your custom profile.

If you have any questions or issues please send us a message on [Slack](https://nf-co.re/join/slack) on the [`#configs` channel](https://nfcore.slack.com/channels/configs).

### Running in the background

Nextflow handles job submissions and supervises the running jobs. The Nextflow process must run until the pipeline is finished.

The Nextflow `-bg` flag launches Nextflow in the background, detached from your terminal so that the workflow does not stop if you log out of your session. The logs are saved to a file.

Alternatively, you can use `screen` / `tmux` or similar tool to create a detached session which you can log back into at a later time.
Some HPC setups also allow you to run nextflow within a cluster job submitted your job scheduler (from where it submits more jobs).

#### Nextflow memory requirements

In some cases, the Nextflow Java virtual machines can start to request a large amount of memory.
We recommend adding the following line to your environment to limit this (typically in `~/.bashrc` or `~./bash_profile`):

```bash
NXF_OPTS='-Xms1g -Xmx4g'
```
