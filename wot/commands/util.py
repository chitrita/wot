CELL_SET_HELP = 'gmt, gmx, or grp file of cell sets.'
CELL_DAYS_HELP = 'File with headers "id" and "day" corresponding to cell id and days'
TMAP_HELP = 'Directory of transport maps as produced by optimal transport'
MATRIX_HELP = 'A matrix with cells on rows and features, such as genes or pathways on columns'
CONFIG_HELP = 'Optional detailed configuration file to specify time-dependant OT parameters'
FORMAT_HELP = 'Output file format'
FORMAT_CHOICES = ['gct', 'h5ad', 'loom', 'txt']


def add_model_arguments(parser):
    parser.add_argument('--matrix', help=MATRIX_HELP, required=True)
    parser.add_argument('--cell_days', help=CELL_DAYS_HELP, required=True)
    parser.add_argument('--config', help=CONFIG_HELP)


def add_ot_parameters_arguments(parser):
    parser.add_argument('--local_pca', type=int, default=30,
                        help='Convert day pairs matrix to local PCA coordinates.'
                             'Set to 0 to disable')
    parser.add_argument('--growth_iters', type=int, default=3,
                        help='Number of growth iterations for learning the growth rate.')
    parser.add_argument('--cell_growth_rates',
                        help='File with "id" and "cell_growth_rate"'
                             'headers corresponding to cell id and growth rate per day.')
    parser.add_argument('--sampling_bias', help='File with "id" and "pp" to correct sampling bias.')
    parser.add_argument('--gene_filter',
                        help='File with one gene id per line to use for computing'
                             'cost matrices (e.g. variable genes)')
    parser.add_argument('--cell_filter',
                        help='File with one cell id per line to include or or a '
                             'python regular expression of cell ids to include')
    parser.add_argument('--cell_day_filter',
                        help='Comma separated list of days to include (e.g. 12,14,16)', type=str)
    parser.add_argument('--scaling_iter', default=3000, help='Number of scaling iterations for OT solver', type=int)
    parser.add_argument('--inner_iter_max', type=int, default=50,
                        help='For OT solver')
    parser.add_argument('--epsilon', type=float, default=0.05,
                        help='Controls the entropy of the transport map. An extremely '
                             'large entropy parameter will give a maximally entropic '
                             'transport map, and an extremely small entropy parameter '
                             'will give a nearly deterministic transport map '
                             '(but could also lead to numerical instability in the algorithm')
    parser.add_argument('--lambda1', type=float, default=1,
                        help='Regularization parameter that controls the '
                             'fidelity of the constraints on p')
    parser.add_argument('--lambda2', type=float, default=50,
                        help='Regularization parameter that controls the '
                             'fidelity of the constraints on q')
    parser.add_argument('--max_threads', type=int, default=1,
                        help='Maximal number of threads to use when parallelizing tmap computation')
    parser.add_argument('--epsilon0', type=float, default=1,
                        help='Warm starting value for epsilon')
    parser.add_argument('--tau', type=float, default=10000)
    parser.add_argument('--ncells', type=int, help='Number of cells to downsample from each timepoint and covariate')
    parser.add_argument('--ncounts', help='Sample ncounts from each cell', type=int)
    parser.add_argument('--force', help='Overwrite existing transport maps if they exist', type=bool, default=False)
    # parser.add_argument('--max_iter', type=int, default=1e7,
    #                     help='Maximum number of scaling iterations. Abort if convergence was not reached')
    # parser.add_argument('--batch_size', type=int, default=50,
    #                     help='Number of scaling iterations to perform between duality gap check')
    # parser.add_argument('--tolerance', type=int, default=1e-2,
    #                     help='Maximal acceptable ratio between the duality gap and the primal objective value')
