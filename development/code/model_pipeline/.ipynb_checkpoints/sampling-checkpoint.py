import os
import sys
import yaml
import psutil
import pandas as pd
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

# create output path
os.makedirs(output_path, exist_ok=True)

# load train-test size parameter
params = yaml.safe_load(open('params.yaml'))['sampling']
bad_flag = params['bad_flag']
test_size = params['test_size']

# import data
temp = pd.read_csv(os.path.join(data_path, 'TREPP_sample-dataset_term-defaults_post_dq_capping.csv'), iterator=True, low_memory=False, chunksize=100000)
df_raw = pd.concat(temp, ignore_index=True)

# free up memory
del temp

# split data
X = df_raw.drop(bad_flag, axis=1)
y = df_raw[bad_flag]

# free up memory
del df_raw

# split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=7, stratify=y)

# free up memory
del X, y

# convert y_train and y_test to dataframes
y_train = y_train.to_frame()
y_test = y_test.to_frame()

# add a label to the data
X_train['label'] = 'train'
X_test['label'] = 'test'

# save data
X_train.to_csv(os.path.join(output_path, 'X_train.csv'), index=False)
X_test.to_csv(os.path.join(output_path, 'X_test.csv'), index=False)
y_train.to_csv(os.path.join(output_path, 'y_train.csv'), index=False)
y_test.to_csv(os.path.join(output_path, 'y_test.csv'), index=False)
