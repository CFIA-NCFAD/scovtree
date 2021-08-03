#!/usr/bin/env python

from pathlib import Path

with open('software_versions.tsv', 'w') as fout:
    fout.write('software\tversion\n')
    for path in Path('.').glob('*.version.txt'):
        software = path.name.replace('.version.txt', '')
        if software == 'pipeline':
            software = 'CFIA-NCFAD/scovtree'
        version = path.read_text().strip()
        fout.write(f'{software}\t{version}\n')
