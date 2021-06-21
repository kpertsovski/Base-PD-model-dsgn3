import os
import sys
import yaml
import json
import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score, roc_curve

# read from command line
data_path = sys.argv[1]
model_path = sys.argv[2]

# load train-test size parameter
params = yaml.safe_load(open('params.yaml'))['model_development']
numerical_columns_as_features = [item+'_transformed' for item in params['numerical_columns_as_features']]
categorical_columns_as_features = [item+'_transformed' for item in params['categorical_columns_as_features']]
model_with_intercept = params['model_with_intercept']

# load data
X_train = pd.read_csv(os.path.join(data_path, 'X_train_transformed.csv'))
y_train = pd.read_csv(os.path.join(data_path, 'y_train_transformed.csv'))
X_test = pd.read_csv(os.path.join(data_path, 'X_test_transformed.csv'))
y_test = pd.read_csv(os.path.join(data_path, 'y_test_transformed.csv'))

# read model
with open(os.path.join(model_path, 'logistic-regression-model.pkl'),'rb') as f:
    results = pickle.load(f)

json_scores = {}
json_plots = {}
def run_model_evaluation(X, y):
    # get label of data
    label = X['label'].unique()[0]
    print('label:', label)
    
    # build features
    X = X[numerical_columns_as_features+categorical_columns_as_features]
    if model_with_intercept.lower()=='yes':
        X = sm.add_constant(X)

    # Area Under the Curve (AUC)
    auc = roc_auc_score(y, results.predict(X))
    # Gini coefficient
    gini = 2*auc - 1

    # save scores
    json_scores['gini_'+label] = gini
    with open(os.path.join(model_path,'gini_values.json'), 'w') as f:
        json.dump(json_scores, f)
    
    # ROC curve
    false_pos_rate, true_pos_rate, thresholds = roc_curve(y, results.predict(X))
    
    # save plots
    json_plots['ROC'+label] = [{
        'fpr': fpr,
        'tpr': tpr,
        'threshold': threshold
        } for fpr, tpr, threshold in zip(false_pos_rate, true_pos_rate, thresholds)]
    with open(os.path.join(model_path,'plots.json'), 'w') as f:
        json.dump(json_plots, f)
    return X, y


# Evaluate model for X_train, y_train
run_model_evaluation(X_train, y_train)

# Evaluate model for X_test, y_test
run_model_evaluation(X_test, y_test)
