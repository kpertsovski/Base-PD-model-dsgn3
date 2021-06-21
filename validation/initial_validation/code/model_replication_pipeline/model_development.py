import os
import sys
import yaml
import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

# create output path
os.makedirs(output_path, exist_ok=True)

# load train-test size parameter
params = yaml.safe_load(open('params.yaml'))['model_development']
numerical_columns_as_features = [item+'_transformed' for item in params['numerical_columns_as_features']]
categorical_columns_as_features = [item+'_transformed' for item in params['categorical_columns_as_features']]
model_with_intercept = params['model_with_intercept']

# load data
X_train = pd.read_csv(os.path.join(data_path, 'X_train_transformed.csv'))
y_train = pd.read_csv(os.path.join(data_path, 'y_train_transformed.csv'))

# build model
X_train = X_train[numerical_columns_as_features+categorical_columns_as_features]

if model_with_intercept.lower()=='yes':
    X_train = sm.add_constant(X_train)

logit_model = sm.Logit(y_train, X_train)
results = logit_model.fit()
print(results.summary())

# save model to csv
df_results = results.summary2().tables[1]
df_results = df_results.rename_axis('Parameter').reset_index()
df_results.to_csv(os.path.join(output_path, 'logistic-regression-model.csv'), index=False)

X_test = pd.read_csv(os.path.join(data_path, 'X_test_transformed.csv'))
X_test = X_test[numerical_columns_as_features+categorical_columns_as_features]
X_test = sm.add_constant(X_test)

# save model to pickle
with open(os.path.join(output_path, 'logistic-regression-model.pkl'),'wb') as f:
    pickle.dump(results, f)