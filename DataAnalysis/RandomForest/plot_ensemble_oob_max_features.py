"""
=============================
OOB Errors for Random Forests
=============================

The ``RandomForestClassifier`` is trained using *bootstrap aggregation*, where
each new tree is fit from a bootstrap sample of the training observations
:math:`z_i = (x_i, y_i)`. The *out-of-bag* (OOB) error is the average error for
each :math:`z_i` calculated using predictions from the trees that do not
contain :math:`z_i` in their respective bootstrap sample. This allows the
``RandomForestClassifier`` to be fit and validated whilst being trained [1].

The example below demonstrates how the OOB error can be measured at the
addition of each new tree during training. The resulting plot allows a
practitioner to approximate a suitable value of ``n_estimators`` at which the
error stabilizes.

.. [1] T. Hastie, R. Tibshirani and J. Friedman, "Elements of Statistical
       Learning Ed. 2", p592-593, Springer, 2009.

"""
import matplotlib.pyplot as plt

from collections import OrderedDict
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
import pandas as pd

# Author: Kian Ho <hui.kian.ho@gmail.com>
#         Gilles Louppe <g.louppe@gmail.com>
#         Andreas Mueller <amueller@ais.uni-bonn.de>
#
# License: BSD 3 Clause

print(__doc__)

RANDOM_STATE = 123

# Import the binary classification dataset
data = pd.read_csv('ebay_data_rf.csv', index_col=False)
data.drop('value', axis=1, inplace=True)

y = data.sellingState
X = data.drop('sellingState', axis=1)

# NOTE: Setting the `warm_start` construction parameter to `True` disables
# support for paralellised ensembles but is necessary for tracking the OOB
# error trajectory during training.
ensemble_clfs = [
    ("RandomForestClassifier, max_features='sqrt'",
        RandomForestClassifier(n_estimators = 140,
                               oob_score=True,
                               random_state=RANDOM_STATE)),
]

# Map a classifier name to a list of (<n_estimators>, <error rate>) pairs.
error_rate = OrderedDict((label, []) for label, _ in ensemble_clfs)

# Range of `n_estimators` values to explore.
min_par = 3
max_par = 21

for label, clf in ensemble_clfs:
    for i in range(min_par, max_par + 1):
        clf.set_params(max_features=i)
        clf.fit(X, y)

        # Record the OOB error for each `max_estimators=i` setting.
        oob_error = 1 - clf.oob_score_
        error_rate[label].append((i, oob_error))

# Generate the "OOB error rate" vs. "n_estimators" plot.
for label, clf_err in error_rate.items():
    xs, ys = zip(*clf_err)
    plt.plot(xs, ys, label=label)

plt.title("Depence of OOB error on number of features at each branch in tree (max_features)")
plt.xlim(min_par, max_par)
plt.xlabel("max_features")
plt.ylabel("OOB error rate")
# plt.legend(loc="upper right")

plt.savefig("../../static/OOB_max_features.png")
