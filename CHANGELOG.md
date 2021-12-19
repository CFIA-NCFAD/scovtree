# CFIA-NCFAD/scovtree: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.6.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.6.0) - [2021-12-14]

### Updates

- Pangolin: 3.1.16 → 3.1.17

### Enhancements

- Nextclade amino acid (AA) deletions also included in AA mutation matrix and can be visualized along with AA substitutions in shiptv tree.
- Users can filter GISAID sequences by collection date (`--gisaid_date_start`, `--gisaid_date_end`), Pangolin lineage (`--gisaid_pangolin_lineages "AY.4,AY44"`), multiple countries and regions.  
- users can specify input sequence metadata table with `--input_metadata` workflow parameter. Must be CSV or TSV file.
- update usage docs to include how to update process containers/packages (e.g. update Pangolin without changing workflow). Borrowed from nf-core/viralrecon.
- Log files now output for most processes.

### Fixes

- allocate more memory for `FILTER_GISAID` process by default (6GB -> 16GB) due to growing size of GISAID DB
- handle all metadata as string so that numeric sequence IDs are not treated as int/float leading to issues with merging of metadata and tracking sequences to keep for further analysis

## [v1.5.1](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.5.1) - [2021-11-12]

### Fixes

* Since Nextflow [v21.06.0-edge](https://github.com/nextflow-io/nextflow/releases/tag/v21.06.0-edge) (commit [7dbf64b](https://github.com/nextflow-io/nextflow/commit/7dbf64bea38907126f44b09a023b8061bf3363d0)), `include` is not allowed within a `workflow` block. Moved `include` from `workflow` block in `main.nf` so that workflow is compatible with later versions of Nextflow.

## [v1.5.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.5.0) - [2021-11-12]

### Updates

* Pangolin version bump to `3.1.16`

## [v1.4.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.4.0) - [2021-08-03]

### Updates

* Pangolin version bump to `3.1.7`
* Updated output documentation
* Forked [nhhaidee/scovtree](https://github.com/nhhaidee/scovtree/) repo to [CFIA-NCFAD](https://github.com/CFIA-NCFAD) organization
* Added test data to [CFIA-NCFAD/nf-test-datasets](https://github.com/CFIA-NCFAD/nf-test-datasets) repo under `scovtree` branch.

## [v1.3.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.3.0) - [July 09 2021]

### :warning: Major enhancements

* Support reading `input_sequences.fasta.gz`
* Pangolin tends to mangle the sequence ID for input FASTA sequences, so It may be necessary to prepare input FASTA sequences for Pangolin analysis so that the results can be easily linked to the original sequences and tree taxa.

## [v1.2.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.2.0) - [July 07 2021]

### :warning: Major enhancements

* Read GISAID data files more efficiently, replacing `tarfile.TarFile.getnames()` method by `tarfile.TarFile.next()` method which is much faster for large file
* Remove duplicate entries during GISAID filtering

## [v1.1.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.1.0) - [July 06 2021]

### :warning: Major enhancements

* This release addresses an enhancement in which low abundance lineages should be better represented in all possible stages. The sampling is done separately for each unique lineage to ensure that each lineage is properly represented and more balanced in Phyolgenetic Analysis.

## [v1.0.0](https://github.com/CFIA-NCFAD/scovtree/releases/tag/1.0.0) - [June 30 2021]

Initial release of CFIA-NCFAD/scovtree, created with the [nf-core](https://nf-co.re/) template and refactored code.
