#!/usr/bin/env python
import logging
from pathlib import Path
from typing import Set, List, Dict

import numpy as np
import pandas as pd
import typer
from rich.console import Console
from rich.logging import RichHandler


def main(nextclade_csv: Path, metadata_output: Path):
    init_logging()
    df_nextclade = pd.read_table(nextclade_csv, sep=';', dtype=str, index_col=0)
    aa_subs: pd.Series = df_nextclade['aaSubstitutions'].str.split(',')
    aa_dels: pd.Series = df_nextclade['aaDeletions'].str.split(',')
    sample_aas = sample_to_aa_mutations(aa_subs, aa_dels)
    samples = list(sample_aas.keys())
    unique_aas = get_sorted_aa_mutations(sample_aas)
    arr_aas = fill_aa_mutation_matrix(sample_aas, samples, unique_aas)
    dfaa = pd.DataFrame(arr_aas, index=samples, columns=unique_aas)
    dfaa.to_csv(metadata_output, sep='\t')


def init_logging():
    from rich.traceback import install
    console = Console(stderr=True, width=120)
    install(show_locals=True, width=120, word_wrap=True, console=console)
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True, console=console)],
    )


def sample_to_aa_mutations(
        aa_subs: pd.Series,
        aa_dels: pd.Series
) -> Dict[str, Set[str]]:
    sample_aas = {}
    for sample, aa_sub, aa_del in zip(aa_subs.index, aa_subs, aa_dels):
        aas = [] if not isinstance(aa_sub, list) else aa_sub
        aad = [] if not isinstance(aa_del, list) else aa_del
        sample_aas[sample] = set(aas) | set(aad)
    return sample_aas


def fill_aa_mutation_matrix(
        sample_aas: Dict[str, Set[str]],
        samples: List[str],
        unique_aas: List[str]
) -> np.ndarray:
    """Fill AA mutation matrix with 1 when AA mutation present in sample"""
    arr_aas = np.zeros((len(sample_aas), len(unique_aas)), dtype='uint8')
    for i, sample in enumerate(samples):
        aas = sample_aas[sample]
        for j, aa in enumerate(unique_aas):
            if aa in aas:
                arr_aas[i, j] = 1
    return arr_aas


def get_sorted_aa_mutations(sample_aas: Dict[str, Set[str]]) -> List[str]:
    unique_aas = set()
    for aas in sample_aas.values():
        unique_aas |= aas
    unique_aas = list(unique_aas)
    unique_aas.sort()
    return unique_aas


if __name__ == '__main__':
    typer.run(main)
