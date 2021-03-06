#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

import anndata
import numpy as np
import pandas as pd

import wot.io


def compute(matrix, gene_sets, out, format, cell_filter=None, background_cell_set=None,
            permutations=None, method=None, n_neighbors=None, drop_frequency=None,
            drop_p_value_threshold=None, gene_set_filter=None, progress=False, neighbors_method=None):
    if out is None:
        out = ''
    use_dask = False
    ds = wot.io.read_dataset(matrix)
    if progress:
        print('Read ' + matrix)
    if cell_filter is not None:
        cell_filter = wot.io.read_sets(cell_filter)
        cells_ids = cell_filter.obs.index.values[np.where(cell_filter.X[:, 0] > 0)[0]]
        cell_filter = ds.obs.index.isin(cells_ids)
        ds = anndata.AnnData(ds.X[cell_filter], ds.obs.iloc[cell_filter], ds.var)

    background_ds = None
    if background_cell_set is not None:
        background_cells_ds = wot.io.read_sets(background_cell_set)
        background_cells_ids = background_cells_ds.obs.index.values[np.where(background_cells_ds.X[:, 0] > 0)[0]]
        cell_filter = ds.obs.index.isin(background_cells_ids)
        background_ds = anndata.AnnData(ds.X[cell_filter], ds.obs.iloc[cell_filter], ds.var)

    gs = wot.io.read_sets(gene_sets, ds.var.index.values)
    if progress:
        print('Read ' + gene_sets)
    if gs.X.shape[1] is 0:
        raise ValueError('No overlap of genes in gene sets and dataset')
    if gene_set_filter is not None:
        if os.path.exists(gene_set_filter):
            set_names = pd.read_table(gene_set_filter, header=None, index_col=0, engine='python', sep='\n').index.values
        else:
            set_names = gene_set_filter.split(',')
        gs_filter = gs.var.index.isin(set_names)
        gs = anndata.AnnData(gs.X[:, gs_filter], gs.obs, gs.var.iloc[gs_filter])
    if gs.X.shape[1] is 0:
        raise ValueError('No gene sets')

    # scores contains cells on rows, gene sets on columns
    for j in range(gs.X.shape[1]):
        if progress and gs.X.shape[1] > 1:
            print(gs.var.index.values[j])
        result = wot.score_gene_sets(dataset_to_score=ds,
                                     gs=gs[:, [j]],
                                     permutations=permutations, method=method, n_neighbors=n_neighbors,
                                     drop_frequency=drop_frequency, drop_p_value_threshold=drop_p_value_threshold,
                                     progress=progress, neighbors_method=neighbors_method)
        column_names = [str(gs.var.index.values[j])]
        if permutations is not None and permutations > 0:
            column_names.append('p_value')
            column_names.append('FDR_BH')
            column_names.append('k')
            column_names.append('n')
            if drop_frequency > 0:
                column_names.append('p_value_ci')
                column_names.append('FDR_BH_low')
                column_names.append('FDR_BH_high')
                x = np.hstack((result['score'], np.vstack(
                    (result['p_value'], result['fdr'], result['k'], result['n'], result['p_value_ci'],
                     result['fdr_low'], result['fdr_high'])).T))
            else:
                x = np.hstack((result['score'], np.vstack(
                    (result['p_value'], result['fdr'], result['k'], result['n'])).T))

        else:
            x = result['score']
        wot.io.write_dataset(ds=anndata.AnnData(X=x, obs=ds.obs, var=pd.DataFrame(index=column_names)),
                             path=out + '_' + column_names[0], output_format=format)
    # import dask.array as da
    # da.to_npy_stack('/Users/jgould/git/wot/bin/data/', result.X, axis=0)


def main(argv):
    parser = argparse.ArgumentParser(description='Compute cell gene set scores')
    parser.add_argument('--matrix', help=wot.commands.MATRIX_HELP, required=True)
    parser.add_argument('--gene_sets',
                        help='Gene sets in gmx, gmt, or grp format', required=True)
    parser.add_argument('--cell_filter', help='Cells to include')
    parser.add_argument('--gene_set_filter', help='Gene sets to include')
    parser.add_argument('--out', help='Output file name prefix')
    # parser.add_argument('--dask', help='Dask scheduler URL')
    parser.add_argument('--format', help=wot.commands.FORMAT_HELP, default='txt', choices=wot.commands.FORMAT_CHOICES)
    parser.add_argument('--nperm', help='Number of permutations', default=10000, type=int)
    parser.add_argument('--method', help='Method to compute gene set scores',
                        choices=['mean_z_score', 'mean', 'mean_rank'], required=True)
    parser.add_argument('--n_neighbors', help='Number of neighbors for sampling', default=20, type=int)
    parser.add_argument('--neighbors_method', help='Method to find nearest neighbors',
                        choices=['mean', 'variance', 'mean_variance'], default='mean')
    parser.add_argument('--drop_p_value_threshold',
                        help='Exclude cells from further permutations when the estimated lower bound of the nominal p-value is >= drop_p_value_threshold',
                        default=0.05, type=float)
    parser.add_argument('--drop_frequency',
                        help='Check the estimated lower bound of the nominal p-value every drop_frequency permutations',
                        default=1000, type=int)
    parser.add_argument('--progress', action='store_true', help='Print progress information')

    args = parser.parse_args(argv)
    if args.out is None:
        args.out = wot.io.get_filename_and_extension(os.path.basename(args.matrix))[0] + '_gene_set_scores'

    # use_dask = args.dask is not None
    # if use_dask:
    #     from dask.distributed import Client
    #
    #     args.format = 'loom'
    #     file_path = args.out + '.loom'
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #     client = Client(args.dask)

    gene_sets = args.gene_sets
    compute(matrix=args.matrix, cell_filter=args.cell_filter, gene_sets=gene_sets, out=args.out,
            format=args.format, permutations=args.nperm, method=args.method, n_neighbors=args.n_neighbors,
            drop_frequency=args.drop_frequency, drop_p_value_threshold=args.drop_p_value_threshold,
            gene_set_filter=args.gene_set_filter, progress=args.progress, neighbors_method=args.neighbors_method)
