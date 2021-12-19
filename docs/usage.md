# CFIA-NCFAD/scovtree: Usage

## Introduction

## Running the pipeline

The pipeline has 2 workflows:

* Phylogenetic analysis with your SARS-CoV-2 sequences

  ```bash
  nextflow run CFIA-NCFAD/scovtree \
    -profile docker \
    --input your-sars-cov-2-sequences.fasta
  ```

* Phylogenetic analysis with your SARS-CoV-2 sequences and GISAID sequences

  ```bash
  nextflow run CFIA-NCFAD/scovtree \
    -profile docker \
    --input your-sars-cov-2-sequences.fasta \
    --input_metadata your-sars-cov-2-sequences-metadata.tsv \
    --gisaid_sequences sequences_fasta_2021_12_01.tar.xz \
    --gisaid_metadata metadata_tsv_2021_12_01.tar.xz
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

First, go to the [CFIA-NCFAD/scovtree releases page](https://github.com/CFIA-NCFAD/scovtree/releases) and find the latest version number - numeric only (eg. `1.3.1`). Then specify this when running the pipeline with `-r` (one hyphen) - eg. `-r 1.5.1`.

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

## Custom configuration

The following section is taken from the [nf-core/viralrecon usage docs](https://github.com/nf-core/viralrecon/blob/master/docs/usage.md#custom-configuration)

### Resource requests

Whilst the default requirements set within the pipeline will hopefully work for most people and with most input data, you may find that you want to customise the compute resources that the pipeline requests. Each step in the pipeline has a default set of requirements for number of CPUs, memory and time. For most of the steps in the pipeline, if the job exits with any of the error codes specified [here](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/conf/base.config#L18) it will automatically be resubmitted with higher requests (2 x original, then 3 x original). If it still fails after the third attempt then the pipeline execution is stopped.

For example, if the nf-core/rnaseq pipeline is failing after multiple re-submissions of the `STAR_ALIGN` process due to an exit code of `137` this would indicate that there is an out of memory issue:

```console
[62/149eb0] NOTE: Process `RNASEQ:ALIGN_STAR:STAR_ALIGN (WT_REP1)` terminated with an error exit status (137) -- Execution is retried (1)
Error executing process > 'RNASEQ:ALIGN_STAR:STAR_ALIGN (WT_REP1)'

Caused by:
    Process `RNASEQ:ALIGN_STAR:STAR_ALIGN (WT_REP1)` terminated with an error exit status (137)

Command executed:
    STAR \
        --genomeDir star \
        --readFilesIn WT_REP1_trimmed.fq.gz  \
        --runThreadN 2 \
        --outFileNamePrefix WT_REP1. \
        <TRUNCATED>

Command exit status:
    137

Command output:
    (empty)

Command error:
    .command.sh: line 9:  30 Killed    STAR --genomeDir star --readFilesIn WT_REP1_trimmed.fq.gz --runThreadN 2 --outFileNamePrefix WT_REP1. <TRUNCATED>
Work dir:
    /home/pipelinetest/work/9d/172ca5881234073e8d76f2a19c88fb

Tip: you can replicate the issue by changing to the process work dir and entering the command `bash .command.run`
```

To bypass this error you would need to find exactly which resources are set by the `STAR_ALIGN` process. The quickest way is to search for `process STAR_ALIGN` in the [nf-core/rnaseq Github repo](https://github.com/nf-core/rnaseq/search?q=process+STAR_ALIGN). We have standardised the structure of Nextflow DSL2 pipelines such that all module files will be present in the `modules/` directory and so based on the search results the file we want is `modules/nf-core/software/star/align/main.nf`. If you click on the link to that file you will notice that there is a `label` directive at the top of the module that is set to [`label process_high`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/modules/nf-core/software/star/align/main.nf#L9). The [Nextflow `label`](https://www.nextflow.io/docs/latest/process.html#label) directive allows us to organise workflow processes in separate groups which can be referenced in a configuration file to select and configure subset of processes having similar computing requirements. The default values for the `process_high` label are set in the pipeline's [`base.config`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/conf/base.config#L33-L37) which in this case is defined as 72GB. Providing you haven't set any other standard nf-core parameters to __cap__ the [maximum resources](https://nf-co.re/usage/configuration#max-resources) used by the pipeline then we can try and bypass the `STAR_ALIGN` process failure by creating a custom config file that sets at least 72GB of memory, in this case increased to 100GB. The custom config below can then be provided to the pipeline via the [`-c`](#-c) parameter as highlighted in previous sections.

```nextflow
process {
    withName: STAR_ALIGN {
        memory = 100.GB
    }
}
```

> **NB:** We specify just the process name i.e. `STAR_ALIGN` in the config file and not the full task name string that is printed to screen in the error message or on the terminal whilst the pipeline is running i.e. `RNASEQ:ALIGN_STAR:STAR_ALIGN`. You may get a warning suggesting that the process selector isn't recognised but you can ignore that if the process name has been specified correctly. This is something that needs to be fixed upstream in core Nextflow.

### Tool-specific options

For the ultimate flexibility, we have implemented and are using Nextflow DSL2 modules in a way where it is possible for both developers and users to change tool-specific command-line arguments (e.g. providing an additional command-line argument to the `STAR_ALIGN` process) as well as publishing options (e.g. saving files produced by the `STAR_ALIGN` process that aren't saved by default by the pipeline). In the majority of instances, as a user you won't have to change the default options set by the pipeline developer(s), however, there may be edge cases where creating a simple custom config file can improve the behaviour of the pipeline if for example it is failing due to a weird error that requires setting a tool-specific parameter to deal with smaller / larger genomes.

The command-line arguments passed to STAR in the `STAR_ALIGN` module are a combination of:

* Mandatory arguments or those that need to be evaluated within the scope of the module, as supplied in the [`script`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/modules/nf-core/software/star/align/main.nf#L49-L55) section of the module file.

* An [`options.args`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/modules/nf-core/software/star/align/main.nf#L56) string of non-mandatory parameters that is set to be empty by default in the module but can be overwritten when including the module in the sub-workflow / workflow context via the `addParams` Nextflow option.

The nf-core/rnaseq pipeline has a sub-workflow (see [terminology](https://github.com/nf-core/modules#terminology)) specifically to align reads with STAR and to sort, index and generate some basic stats on the resulting BAM files using SAMtools. At the top of this file we import the `STAR_ALIGN` module via the Nextflow [`include`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/subworkflows/nf-core/align_star.nf#L10) keyword and by default the options passed to the module via the `addParams` option are set as an empty Groovy map [here](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/subworkflows/nf-core/align_star.nf#L5); this in turn means `options.args` will be set to empty by default in the module file too. This is an intentional design choice and allows us to implement well-written sub-workflows composed of a chain of tools that by default run with the bare minimum parameter set for any given tool in order to make it much easier to share across pipelines and to provide the flexibility for users and developers to customise any non-mandatory arguments.

When including the sub-workflow above in the main pipeline workflow we use the same `include` statement, however, we now have the ability to overwrite options for each of the tools in the sub-workflow including the [`align_options`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/workflows/rnaseq.nf#L225) variable that will be used specifically to overwrite the optional arguments passed to the `STAR_ALIGN` module. In this case, the options to be provided to `STAR_ALIGN` have been assigned sensible defaults by the developer(s) in the pipeline's [`modules.config`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/conf/modules.config#L70-L74) and can be accessed and customised in the [workflow context](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/workflows/rnaseq.nf#L201-L204) too before eventually passing them to the sub-workflow as a Groovy map called `star_align_options`. These options will then be propagated from `workflow -> sub-workflow -> module`.

As mentioned at the beginning of this section it may also be necessary for users to overwrite the options passed to modules to be able to customise specific aspects of the way in which a particular tool is executed by the pipeline. Given that all of the default module options are stored in the pipeline's `modules.config` as a [`params` variable](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/conf/modules.config#L24-L25) it is also possible to overwrite any of these options via a custom config file.

Say for example we want to append an additional, non-mandatory parameter (i.e. `--outFilterMismatchNmax 16`) to the arguments passed to the `STAR_ALIGN` module. Firstly, we need to copy across the default `args` specified in the [`modules.config`](https://github.com/nf-core/rnaseq/blob/4c27ef5610c87db00c3c5a3eed10b1d161abf575/conf/modules.config#L71) and create a custom config file that is a composite of the default `args` as well as the additional options you would like to provide. This is very important because Nextflow will overwrite the default value of `args` that you provide via the custom config.

As you will see in the example below, we have:

* appended `--outFilterMismatchNmax 16` to the default `args` used by the module.
* changed the default `publish_dir` value to where the files will eventually be published in the main results directory.
* appended `'bam':''` to the default value of `publish_files` so that the BAM files generated by the process will also be saved in the top-level results directory for the module. Note: `'out':'log'` means any file/directory ending in `out` will now be saved in a separate directory called `my_star_directory/log/`.

```nextflow
params {
    modules {
        'star_align' {
            args          = "--quantMode TranscriptomeSAM --twopassMode Basic --outSAMtype BAM Unsorted --readFilesCommand zcat --runRNGseed 0 --outFilterMultimapNmax 20 --alignSJDBoverhangMin 1 --outSAMattributes NH HI AS NM MD --quantTranscriptomeBan Singleend --outFilterMismatchNmax 16"
            publish_dir   = "my_star_directory"
            publish_files = ['out':'log', 'tab':'log', 'bam':'']
        }
    }
}
```

### Updating containers

The [Nextflow DSL2](https://www.nextflow.io/docs/latest/dsl2.html) implementation of this pipeline uses one container per process which makes it much easier to maintain and update software dependencies. If for some reason you need to use a different version of a particular tool with the pipeline then you just need to identify the `process` name and override the Nextflow `container` definition for that process using the `withName` declaration. For example, in the [nf-core/viralrecon](https://nf-co.re/viralrecon) pipeline a tool called [Pangolin](https://github.com/cov-lineages/pangolin) has been used during the COVID-19 pandemic to assign lineages to SARS-CoV-2 genome sequenced samples. Given that the lineage assignments change quite frequently it doesn't make sense to re-release the nf-core/viralrecon everytime a new version of Pangolin has been released. However, you can override the default container used by the pipeline by creating a custom config file and passing it as a command-line argument via `-c custom.config`.

1. Check the default version used by the pipeline in the module file for [Pangolin](https://github.com/nf-core/viralrecon/blob/a85d5969f9025409e3618d6c280ef15ce417df65/modules/nf-core/software/pangolin/main.nf#L14-L19)
2. Find the latest version of the Biocontainer available on [Quay.io](https://quay.io/repository/biocontainers/pangolin?tag=latest&tab=tags)
3. Create the custom config accordingly:

    * For Docker:

        ```nextflow
        process {
            withName: PANGOLIN {
                container = 'quay.io/biocontainers/pangolin:3.0.5--pyhdfd78af_0'
            }
        }
        ```

    * For Singularity:

        ```nextflow
        process {
            withName: PANGOLIN {
                container = 'https://depot.galaxyproject.org/singularity/pangolin:3.0.5--pyhdfd78af_0'
            }
        }
        ```

    * For Conda:

        ```nextflow
        process {
            withName: PANGOLIN {
                conda = 'bioconda::pangolin=3.0.5'
            }
        }
        ```

> **NB:** If you wish to periodically update individual tool-specific results (e.g. Pangolin) generated by the pipeline then you must ensure to keep the `work/` directory otherwise the `-resume` ability of the pipeline will be compromised and it will restart from scratch.

## Running in the background

Nextflow handles job submissions and supervises the running jobs. The Nextflow process must run until the pipeline is finished.

The Nextflow `-bg` flag launches Nextflow in the background, detached from your terminal so that the workflow does not stop if you log out of your session. The logs are saved to a file.

Alternatively, you can use `screen` / `tmux` or similar tool to create a detached session which you can log back into at a later time.
Some HPC setups also allow you to run nextflow within a cluster job submitted your job scheduler (from where it submits more jobs).

## Nextflow memory requirements

In some cases, the Nextflow Java virtual machines can start to request a large amount of memory.
We recommend adding the following line to your environment to limit this (typically in `~/.bashrc` or `~./bash_profile`):

```bash
NXF_OPTS='-Xms1g -Xmx4g'
```
