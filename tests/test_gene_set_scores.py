#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import os
import subprocess
import unittest

import anndata
import numpy as np
import pandas as pd
import scipy.sparse

import wot


class TestGeneSetScores(unittest.TestCase):

    def test_score_gene_set_command(self):
        subprocess.call(args=['wot', 'gene_set_scores',
                              '--matrix',
                              os.path.abspath(
                                  'inputs/score_gene_sets/matrix.txt'),
                              '--gene_sets', os.path.abspath(
                'inputs/score_gene_sets/gene_sets.gmx'),
                              '--out', 'test_gene_set_test_output',
                              '--method', 'mean', '--format', 'txt'],
                        cwd=os.getcwd(),
                        stderr=subprocess.STDOUT)
        set_names = ['s1', 's2', 's3']
        scores = np.array([[1, 0, 1.5], [4, 0, 4.5]])
        for i in range(len(set_names)):
            output_file = 'test_gene_set_test_output_' + set_names[i] + '.txt'
            output = pd.read_table(output_file, index_col=0)
            np.testing.assert_array_equal(output[set_names[i]].values, scores[:, i])
            os.remove(output_file)

    def test_score_gene_sets_drop(self):
        ds = anndata.AnnData(X=np.array([[1.0, 2, 3, 4, 5, 6, 7, 8, 9, 10]]), obs=None,
                             var=None)

        gs = anndata.AnnData(X=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.uint8).T, obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method=None, permutations=100,
                                     random_state=1234, drop_frequency=100, drop_p_value_threshold=1)
        self.assertEqual(result['k'][0], 15)

    def test_p_value1(self):
        ds = anndata.AnnData(X=np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]), obs=None, var=None)
        gs = anndata.AnnData(X=np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=np.uint8).T, obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method=None, permutations=10,
                                     drop_frequency=0, random_state=1234)
        np.testing.assert_array_equal(result['p_value'][0], 11.0 / 12.0)

    def test_p_value2(self):
        ds = anndata.AnnData(X=np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]), obs=None, var=None)
        gs = anndata.AnnData(X=np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.uint8).T, obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method=None, permutations=45,
                                     drop_frequency=0, random_state=1234)
        np.testing.assert_array_equal(result['k'][0], (
                np.mean(np.array(list(itertools.combinations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 2))),
                        axis=1) >= 5.5).sum())

    def test_score_gene_sets_no_drop(self):
        ds = anndata.AnnData(X=np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]), obs=None, var=None)

        gs = anndata.AnnData(X=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.uint8).T, obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method=None, permutations=1000,
                                     random_state=1234, drop_frequency=0)
        self.assertEqual(result['k'][0], 116)

    def test_score_gene_sets_sparse_ds(self):
        ds = anndata.AnnData(
            x=scipy.sparse.csr_matrix(np.array([[0, 0, 0, 4, 5, 6, 7, 8, 9, 10]])),
            obs=None,
            var=None)

        gs = anndata.AnnData(X=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.uint8).T, obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method=None, permutations=100,
                                     random_state=1234, drop_frequency=100, drop_p_value_threshold=1,
                                     smooth_p_values=False)
        self.assertEqual(result['k'][0], 15)

    def test_score_gene_sets_sparse_ds_zscore(self):
        ds = anndata.AnnData(
            x=scipy.sparse.csr_matrix(np.array([[0, 0, 0, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 5, 6, 7, 9, 9, 19, 11]])),
            obs=None,
            var=None)

        gs = anndata.AnnData(X=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.uint8).T, obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method='mean_z_score', permutations=100,
                                     random_state=1234, drop_frequency=100, drop_p_value_threshold=1,
                                     smooth_p_values=False)

        self.assertEqual(result['k'][0], 100)

    def test_score_gene_sets_sparse_gs(self):
        ds = anndata.AnnData(
            x=np.array([[0, 0, 0, 4, 5, 6, 7, 8, 9, 10]]),
            obs=None,
            var=None)

        gs = anndata.AnnData(X=scipy.sparse.csr_matrix(np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]], dtype=np.uint8).T),
                             obs=None, var=None)
        result = wot.score_gene_sets(dataset_to_score=ds, gs=gs, method=None, permutations=100,
                                     random_state=1234, drop_frequency=100, drop_p_value_threshold=1,
                                     smooth_p_values=False)

        self.assertEqual(result['k'][0], 15)

    def test_score_gene_sets_basic(self):
        ds = anndata.AnnData(X=np.array([[1.0, 2.0, 3, 0], [4, 5, 6.0, 0]]),
                             obs=pd.DataFrame(
                                 index=['c1', 'c2']),
                             var=pd.DataFrame(
                                 index=['g1', 'g2',
                                        'g3', 'g4']))

        gs = anndata.AnnData(X=np.array([[1, 0, 1], [0, 0, 1], [0, 0, 0], [0, 1, 0]], dtype=np.uint8),
                             obs=pd.DataFrame(
                                 index=['g1', 'g2', 'g3', 'g4']),
                             var=pd.DataFrame(
                                 index=['s1', 's2', 's3']))

        expected = np.array([[1, 0, 1.5], [4, 0, 4.5]])
        scores = []
        for j in range(gs.X.shape[1]):
            result = wot.score_gene_sets(dataset_to_score=ds,
                                         gs=anndata.AnnData(gs.X[:, [j]], gs.obs, gs.var.iloc[[j]]), method=None,
                                         permutations=10)
            scores.append(result['score'])
        np.testing.assert_array_equal(np.hstack(scores), expected)


if __name__ == '__main__':
    unittest.main()
