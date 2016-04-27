import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.feature_selection import VarianceThreshold
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, roc_auc_score
import pprint as pp
from bokeh.charts import Bar, BoxPlot, output_file, show
from bokeh.models import Range1d
from bokeh.io import hplot
from bokeh.plotting import figure
from datetime import datetime
import time

#######################################################
# Read in the data
#######################################################

# Read in the pandas.DataFrame from csv
data = pd.read_csv('ebay_data_rf.csv', index_col=False)
data.drop('value', axis=1, inplace=True)

#######################################################
# Remove columns with zero variance
#######################################################

selector = VarianceThreshold()
selector.fit_transform(data)

#######################################################
# Separate target variable (saleStatus)
#######################################################

y = data.sellingState
data.drop('sellingState', axis=1, inplace=True)

#######################################################
# Break data into train and test sets
#######################################################

X_train, X_test, y_train, y_test = train_test_split(
    data, y, test_size=0.25, random_state=7
)

#######################################################
# Train the random forest classifier
#######################################################

n_estimators = 50
weights = {0: 2.5, 1: 1}
clf = RandomForestClassifier(n_estimators,
                             max_features=None,
                             oob_score=True,
                             class_weight=weights,
                             warm_start=False)

clf.fit(X_train,y_train)

#######################################################
# Test on the test set
#######################################################

# Test on the training set:
y_test_pred = clf.predict(X_test)

# Print the confusion matrix
pp.pprint(confusion_matrix(y_test, y_test_pred))

# Calculate the roc_auc score
print('Overall AUC:', roc_auc_score(y_test, clf.predict_proba(X_test)[:,1]))

#######################################################
# Feature importances
#######################################################

cols = data.columns
feature_scores = clf.feature_importances_

score_card = pd.DataFrame.from_items([('Features', cols),('Scores', feature_scores)])

score_card.sort_values(by = 'Scores', inplace=True, ascending=False)

print(score_card)

