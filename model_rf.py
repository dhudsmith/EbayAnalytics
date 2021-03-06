import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.externals import joblib
import pprint as pp

#######################################################
# Read in the data
#######################################################

# Read in the pandas.DataFrame from csv
data = pd.read_csv('../../Data/ebay_data_rf.csv', index_col=False)

print("Initial shape: ", data.shape)

#######################################################
# Separate target variable (saleStatus)
#######################################################

y = data.sellingState
# data.drop(['sellingState'], axis=1, inplace=True)
data.drop(['sellingState'], axis=1, inplace=True)

#######################################################
# Break data into train and test sets
#######################################################

X_train, X_test, y_train, y_test = train_test_split(
    data, y, test_size=0.1, random_state=7
)

#######################################################
# Train the model
#######################################################

n_estimators = 300
max_features = None
weights = {0: 1, 1: 1}
clf = RandomForestClassifier(n_estimators,
                             max_features=max_features,
                             oob_score=False,
                             class_weight=weights,
                             n_jobs=4,
                             warm_start=False)

# clf = GradientBoostingClassifier(loss='exponential',
#                                  n_estimators = n_estimators,
#                                  max_leaf_nodes=20)

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

#######################################################
# Persist the model
#######################################################

joblib.dump(clf, '../../static/model_pkl/rf_model_april_27_2016.pkl',protocol=2)
