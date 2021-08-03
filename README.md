# CFIA-NCFAD/scovtree

**SARS-CoV-2 phylogenetic analysis pipeline**.

[![Nextflow](https://img.shields.io/badge/nextflow%20DSL2-%E2%89%A521.04.0-23aa62.svg?labelColor=000000)](https://www.nextflow.io/)
[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg)](https://bioconda.github.io/)

## Introduction

**CFIA-NCFAD/scovtree** is a bioinformatics pipeline for [SARS-CoV-2] phylogenetic analysis.
Given an input FASTA file with SARS-CoV-2 sequences, this workflow will generate a maximum-likelihood phylogenetic tree (using [IQ-TREE] from a [MAFFT] or [Nextalign] multiple sequence alignment) and interactive HTML tree visualization ([shiptv]).

This pipeline also allows you to visualize your sequences along with the most closely SARS-CoV-2 sequences from [GISAID][] (if both the GISAID sequences and metadata `.tar.xz` files are provided). Amino acid mutations can also be determined using [Nextclade] and shown in the tree visualization.

The pipeline is built using [Nextflow], a workflow tool to run tasks across multiple compute infrastructures in a very portable manner. It comes with docker containers making installation trivial and results highly reproducible.

## Quick Start

1. Install [`nextflow`](https://nf-co.re/usage/installation)

2. Install any of [`Docker`](https://docs.docker.com/engine/installation/), [`Singularity`](https://www.sylabs.io/guides/3.0/user-guide/) for full pipeline reproducibility _(please only use [`Conda`](https://conda.io/miniconda.html) as a last resort; see [docs](https://nf-co.re/usage/configuration#basic-configuration-profiles))_

3. Download the pipeline and test it on a minimal dataset with a single command:

    ```bash
    nextflow run CFIA-NCFAD/scovtree -profile test,<docker/singularity/conda>
    ```

4. Start running your own analysis!

    * Typical command for phylogenetic analysis:

        ```bash
        nextflow run CFIA-NCFAD/scovtree -profile <docker/singularity/conda> \
            --input your-sars-cov-2-sequences.fasta
        ```

    * Typical command for phylogenetic analysis with GISAID SARS-CoV-2 data:

        ```bash
        nextflow run CFIA-NCFAD/scovtree -profile <docker/singularity/conda> \
            --input your-sars-cov-2-sequences.fasta \
            --gisaid_sequences sequences_fasta_2021_06_14.tar.xz \
            --gisaid_metadata metadata_tsv_2021_06_14.tar.xz
        ```

## Credits

`CFIA-NCFAD/scovtree` was originally written by [Hai Nguyen].

Contributors:

* [Peter Kruczkiewicz] for workflow conceptualization and software development.
* [jts/ncov-tools] for `bin/align2alleles.py` and `bin/phylogenetic_tree_snps.r` to create phylogenetic tree with SNPs highlighted using R [ggtree]

## Contributions and Support

If you would like to contribute to this pipeline, please see the [contributing guidelines](.github/CONTRIBUTING.md).

For further information or help, don't hesitate to get in touch on the [Slack `#scovtree` channel](https://nfcore.slack.com/channels/scovtree) (you can join with [this invite](https://nf-co.re/join/slack)).

## Citations

<!-- TODO nf-core: Add citation for pipeline after first release. Uncomment lines below and update Zenodo doi. -->
<!-- If you use  CFIA-NCFAD/scovtree for your analysis, please cite it using the following doi: [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX) -->
This pipeline tries to follow the best practices for Nextflow workflow development and deployment set by `nf-core`. You can cite the `nf-core` publication as follows:

> **The nf-core framework for community-curated bioinformatics pipelines.**
>
> Philip Ewels, Alexander Peltzer, Sven Fillinger, Harshil Patel, Johannes Alneberg, Andreas Wilm, Maxime Ulysse Garcia, Paolo Di Tommaso & Sven Nahnsen.
>
> _Nat Biotechnol._ 2020 Feb 13. doi: [10.1038/s41587-020-0439-x](https://dx.doi.org/10.1038/s41587-020-0439-x).

In addition, references of tools and data used in this pipeline are as follows:

* [nf-core]
* [jts/ncov-tools]
* [IQ-TREE]
* [Nextalign]
* [Nextclade]
* [MAFFT]
* [shiptv]
* [Pangolin]
* [ggtree]
* [GISAID]
* [SARS-CoV-2]

## License

Copyright 2021 Canadian Food Inspection Agency of Canada, Government of Canada.

Distributed under the MIT license.

<!-- TODO nf-core: Add bibliography of tools and data used in your pipeline -->

[Nextflow]: https://www.nextflow.io/
[nf-core]: https://nf-co.re/
[jts/ncov-tools]: https://github.com/jts/ncov-tools
[IQ-TREE]: http://www.iqtree.org/
[Nextstrain]: https://nextstrain.org/
[Nextalign]: https://github.com/nextstrain/nextclade/tree/master/packages/nextalign_cli
[Nextclade]: https://github.com/nextstrain/nextclade/tree/master/packages/nextclade_cli
[MAFFT]: https://mafft.cbrc.jp/alignment/software/
[shiptv]: https://github.com/peterk87/shiptv
[Pangolin]: https://github.com/cov-lineages/pangolin/
[ggtree]: https://bioconductor.org/packages/release/bioc/html/ggtree.html
[Peter Kruczkiewicz]: https://github.com/peterk87/
[Hai Nguyen]: https://github.com/nhhaidee/
[GISAID]: https://www.gisaid.org/
[SARS-CoV-2]: https://www.ncbi.nlm.nih.gov/nuccore/MN908947.3/
