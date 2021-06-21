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
params = yaml.safe_load(open('params.yaml'))['model_testing']
benchmark = params['benchmark']

# load front office model coefficients
logit_model_benchmark = pd.read_csv(os.path.join(data_path, benchmark))

# load replicated model
logit_model_replication = pd.read_csv(os.path.join(model_path, 'logistic-regression-model.csv'))

# merge and calculate difference in coefficients and std. error
df_merged = pd.merge(logit_model_benchmark, logit_model_replication, how='outer', on='Parameter', suffixes=('_development','_validation'))
df_merged['Parameter'] = df_merged['Parameter'].str.replace(r'_transformed', '')
df_merged['Coef._diff'] = df_merged['Coef._development'] - df_merged['Coef._validation']

df_merged = df_merged[['Parameter','Coef._development','Coef._validation','Coef._diff']]
print(df_merged)

df_merged.to_json(os.path.join("5_1_3_model_coefficient_comparison", "output", "model_coefficient_comparison.json"), orient="records")