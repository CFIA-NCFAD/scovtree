#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.logging import RichHandler


def main(
        metadata_input: Path,
        pangolin_report: Path,
        metadata_output: Path = typer.Option(Path('metadata.merged.tsv')),
        aa_mutation_matrix: Optional[Path] = typer.Option(None, help='Amino acid mutation matrix TSV'),
        select_metadata_fields: Optional[str] = typer.Option(None,
                                                             help='Comma-delimited list of metadata fields to output. '
                                                                  'If unset, all metadata fields will be output.'),
        user_metadata: Optional[Path] = typer.Option(None, help='User sequences metadata CSV or tab-delimited table.')
):
    """Merge a metadata table, Pangolin results table and AA mutation matrix into one table."""
    from rich.traceback import install
    install(show_locals=True, width=120, word_wrap=True, console=Console(stderr=True))
    logging.basicConfig(
        format="%(message)s",
        datefmt="[%Y-%m-%d %X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True,
                              tracebacks_show_locals=True,
                              console=Console(stderr=True))],
    )
    df_metadata = pd.read_table(metadata_input, dtype=str)
    df_metadata.set_index(df_metadata.columns[0], inplace=True)
    logging.info(f'Read metadata table "{metadata_input}" with '
                 f'{df_metadata.shape[0]} rows and {df_metadata.shape[1]} columns')
    if select_metadata_fields:
        logging.info(f'Selecting specified metadata fields/columns from '
                     f'"{metadata_input}": {select_metadata_fields}')
        df_metadata = select_fields(df_metadata, select_metadata_fields)
    if user_metadata:
        logging.info(f'Reading user metadata table from "{user_metadata}". Assuming first column contains user '
                     f'sequence IDs/names.')
        df_user = read_user_metadata(user_metadata)
        if df_user is not None:
            logging.info(f'Combining user metadata table with shape {df_user.shape} '
                         f'(columns={df_user.columns.tolist()}) with GISAID metadata table '
                         f'(shape={df_metadata.shape}).')
            df_metadata = df_user.combine_first(df_metadata)
        else:
            logging.warning(f'Empty user metadata table from "{user_metadata}"')
    dfs = [df_metadata]
    df_pangolin = read_pangolin_report(pangolin_report)
    dfs.append(df_pangolin)
    if aa_mutation_matrix:
        dfs.append(pd.read_table(aa_mutation_matrix, index_col=0, dtype=str))
    logging.info(f'Merging {len(dfs)} dataframes on index')
    df_merged = pd.concat(dfs, axis=1)
    if 'Pango_lineage' in df_merged.columns:
        df_merged['Pango_lineage'] = df_merged['Pango_lineage'].combine_first(df_pangolin['lineage'])
    if 'Pangolin_version' in df_merged.columns:
        df_merged['Pangolin_version'] = df_merged['Pangolin_version'].combine_first(df_pangolin['pangoLEARN_version'])
    logging.info(f'Writing merged dataframe with shape {df_merged.shape} to "{metadata_output}".')
    df_merged.to_csv(metadata_output, sep='\t', index=True)
    logging.info(f'Wrote merged dataframe with shape {df_merged.shape} to "{metadata_output}".')


def read_user_metadata(user_metadata: Path) -> Optional[pd.DataFrame]:
    ext = user_metadata.suffix
    if ext == '.csv':
        df_user = pd.read_csv(user_metadata, dtype=str)
    elif ext in ['.tsv', '.txt']:
        df_user = pd.read_table(user_metadata, dtype=str)
    else:
        logging.warning(f'Trying to read "{user_metadata}" as tab-delimited table.')
        try:
            df_user = pd.read_table(user_metadata, dtype=str)
        except Exception as e:
            logging.error(f'Could not read "{user_metadata}" as tab-delimited table. Error: {e}')
            df_user = None
    if df_user is None:
        return None
    if df_user.empty:
        return None
    df_user.set_index(df_user.columns[0], inplace=True)
    return df_user


def select_fields(df_metadata: pd.DataFrame, select_metadata_fields: str) -> pd.DataFrame:
    metadata_columns = set(df_metadata.columns)
    columns = [x.strip() for x in select_metadata_fields.split(',') if x.strip() in metadata_columns]
    logging.info(f'Selecting columns "{",".join(columns)}"')
    logging.info(f'Metadata table shape before selecting specific columns: {df_metadata.shape}')
    df_metadata = df_metadata[columns]
    logging.info(f'Metadata table shape after selecting specific columns: {df_metadata.shape}')
    return df_metadata


def read_pangolin_report(pangolin_report: Path) -> pd.DataFrame:
    df = pd.read_csv(pangolin_report, dtype=str)
    df.set_index(df.columns[0], inplace=True)
    return df


if __name__ == '__main__':
    typer.run(main)
