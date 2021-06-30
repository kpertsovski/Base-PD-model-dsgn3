
"""
Title: Data Quality tests for Trepp
Description: Performs basic data quality checks on development data set
Date: 01/20/2021
Version: 0.0.1
Status: Development
"""



import os
import sys
import yaml
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from numpy import mean
from numpy import std
import seaborn as sns


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

sns.set_style('whitegrid')

sys.path.append(os.getcwd()+"/Internal Library")

print(sys.path)
from data_utils import *

import warnings
warnings.filterwarnings('ignore')

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

PATH = os.getcwd()+"/5_1_1_data_quality/output/"


# ## 1. Model Input

# Reading the data into a pandas dataframe
temp = pd.read_csv(os.path.join(data_path, 'TREPP_sample-dataset_term-defaults.csv'), iterator=True, low_memory=False, chunksize=100000)
df = pd.concat(temp, ignore_index=True)

# Test for user input
input("\nPlease select all variables in the file '/../../data/raw/dq_checks.xlsx' eligible for data quality checks and press 'Enter' to continue.")

dq_checks = pd.read_excel(os.getcwd()+"/../../data/raw/dq_checks.xlsx")

variables_for_data_quality_check = dq_checks.loc[dq_checks['dq_check'].str.lower()=='yes']['Variable'].to_list()
print('===>> Selected variables for data quality check: {variables} \n'.format(variables=variables_for_data_quality_check))

# Drop the unnecessary index column

df = df.drop(['Unnamed: 0'], axis=1)

# Filter data according to selected variables in dq_checks.xlsx file
df_clean = df.copy()
df = df[variables_for_data_quality_check]

# ## 2. Data Analysis

# ### 2.1 Data Profiling - missing values, outliers, and highly-correlated varaibles

desc = df.describe(include='all')
fname = PATH + 'descriptive_stats.json'
print(fname+' ...')
if os.path.exists(fname):
    os.remove(fname)
    print("The file already exists, will be overwritten.")
else:
    print("New file created.")

# Data Representation
desc.reset_index(inplace=True)
desc = desc.rename(columns={"index": "metrics"})
desc = desc.fillna("N/A")

# load train-test size parameter
params = yaml.safe_load(open('params.yaml'))['model_development']
numerical_columns_as_features = [item for item in params['numerical_columns_as_features']]
categorical_columns_as_features = [item for item in params['categorical_columns_as_features']]
dpVar =yaml.safe_load(open('params.yaml'))['sampling']['bad_flag']

desc = desc[["metrics"] + numerical_columns_as_features + categorical_columns_as_features + [dpVar]]

#desc.to_excel(fname)

#Saving JSON file
desc.to_json(os.path.join(PATH, 'descriptive_stats.json'), orient="records")


# #### missing value of the raw dataset



fname = PATH + 'missing_values.json'
print(fname+' ...')
if os.path.exists(fname):
    os.remove(fname)
    print("The file already exists, will be overwritten.")
else:
    print("New file created.")

# Data Representation    
miss = missing_value_statistic(df)
miss['% Missing'] = miss['% Missing'].round(decimals=2)
miss['% Missing'] =  miss['% Missing'].astype(str) + '%'
miss
#miss(df).to_excel(fname)

#Saving JSON file
miss.to_json(os.path.join(PATH, 'missing_values.json'), orient="records")


# ### 2.1.2 outlier detection

# In this section, we evaluate the dataset for outliers. These tests are only run on the selected variables and only if they are numerical.

# Creating seperate lists for numeric and non-numeric features
columns_numeric, columns_nonnumeric = data_types(df)

# define subset of numeric variables to include in analysis
vars_numeric = [item for item in variables_for_data_quality_check if item in columns_numeric]

# create box plots for numeric variables
#string = ""
for col in vars_numeric:
    plot_box_var(df, col)   
    var = str(col)
    fig = plt.gcf()
    fname = PATH +var+'.png'
    fig.savefig(fname)
#    string = string + '<img src="'+fname+'" alt="'+var+'" width="700">\n'


outliers = df[vars_numeric].apply(outliers_detection)

fname = PATH + 'outliers.json'
print(fname+' ...')
if os.path.exists(fname):
    os.remove(fname)
    print("The file already exists, will be overwritten.")
else:
    print("New file created.")


#outliers.to_excel(fname)

#Saving JSON file
outliers.to_json(os.path.join(PATH, 'outliers.json'), orient="records")


# ### 2.1.3 Correlation Heatmap

# We examine the correlation among features using correlation heatmap. specifically we look for "hot spots" in the correlation heatmap. The correlation among features, and correlation between features and the target will inform the feature engineering process.


# Correlation matrix

cm=df[vars_numeric].corr()
fig = sns.heatmap(cm,square=True)
#plt.yticks(rotation=0)
#plt.yticks(rotation=0)

fig = fig.get_figure()
fname = PATH +"correlation_heatmap"+'.png'
fig.savefig(fname)

fname = PATH + 'correlations.json'
print(fname+' ...')
if os.path.exists(fname):
    os.remove(fname)
    print("The file already exists, will be overwritten.")
else:
    print("New file created.")
#cm.to_excel(fname)

#Saving JSON file
cm.to_json(os.path.join(PATH, 'correlations.json'), orient="records")


# currently no manipulations on the data are performed. outlier removal/capping or removing variables with too many missing values could be considered
df_clean.to_csv(os.path.join(output_path, 'TREPP_sample-dataset_term-defaults_post_dq.csv'))

