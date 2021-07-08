# nhhaidee/scovtree: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.2.0](https://github.com/nhhaidee/scovtree/releases/tag/1.2.0) - [July 07 2021]

### :warning: Major enhancements

* Read GISAID data files more efficiently, replacing `tarfile.TarFile.getnames()` method by `tarfile.TarFile.next()` method which is much faster for large file
* Remove duplicate entries during GISAID filtering

## [v1.1.0](https://github.com/nhhaidee/scovtree/releases/tag/1.1.0) - [July 06 2021]

### :warning: Major enhancements

* This release addresses an enhancement in which low abundance lineages should be better represented in all possible stages. The sampling is done separately for each unique lineage to ensure that each lineage is properly represented and more balanced in Phyolgenetic Analysis.

## [v1.0.0](https://github.com/nhhaidee/scovtree/releases/tag/1.0.0) - [June 30 2021]

Initial release of nhhaidee/scovtree, created with the [nf-core](https://nf-co.re/) template and refactored code.
