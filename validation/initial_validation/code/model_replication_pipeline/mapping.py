# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 12:31:11 2021

@author: Dina Akimova
"""

import os
import sys
import yaml
import json
import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve

# read from command line
data_path = sys.argv[1]
model_path = sys.argv[2]
mapping_path = sys.argv[3]

#data path manual input 
#data_path = '~/Rekha/Doc-Demo-PD-model-dsgn3/development/data/interim/'
#model_path = '~/Rekha/Doc-Demo-PD-model-dsgn3/development/data/processed/logistic-regression-model.pkl'
#output_path = '~/Rekha/Doc-Demo-PD-model-dsgn3/development/data/processed/'
#print(data_path)
#print(model_path)

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

#load mapping
mapping = pd.read_csv(os.path.join(mapping_path, 'mapping.csv'))

#print(os.path.join(data_path, 'y_test_transformed.csv'))
# read model
with open(os.path.join(model_path, 'logistic-regression-model.pkl'),'rb') as f:
    results = pickle.load(f)

json_scores = {}
rating = []
def get_score(X, mapping):
    label = X['label'].unique()[0]
    print('label:', label)
    
    # build features
    X = X[numerical_columns_as_features+categorical_columns_as_features]
    if model_with_intercept.lower()=='yes':
        X = sm.add_constant(X)
    
    #get probability
    probability = results.predict(X)
    rating = probability.copy()
    prob = mapping['MaxProb'].tolist()
    rat = mapping['Rating'].tolist()
   
    for i in range(len(probability)):
        if probability[i] < prob[0]:
            rating[i] = "AAA"
        if probability[i] > prob[16]:
            rating[i] = "CCC"
        else:
            for k in range(len(prob)):
                if prob[k-1] <= probability[i] < prob[k]:
                    rating[i] = rat[k]
    probability = pd.DataFrame(probability, columns=['Probability'])
    rating = pd.DataFrame(rating, columns=['Rating'])
    rating_sum = pd.merge(probability, rating, right_index=True, left_index=True)        
    return rating_sum

def plot_data(X, mapping, name):
    rating_sum = get_score(X, mapping)
    #histograms
    total_group = rating_sum.groupby(['Rating']).size().to_frame('Size').reset_index()
    
    total= pd.DataFrame(mapping['Rating'])
    total['Size'] = total.Rating.map(total_group.set_index('Rating')['Size']).fillna(0)
    total_group = total.copy()
    
    plt.figure(figsize=(12,12))
    plt.bar(total_group['Rating'], total_group['Size'])
    plt.savefig(name +'_hist_all_count.png')
    plt.close()

    total_percentage = total_group.copy()
    total_percentage['Percentage'] = total_group['Size'].transform(lambda x: x/sum(x))
    plt.figure(figsize=(12,12))
    plt.bar(total_percentage['Rating'], total_percentage['Percentage'])
    plt.savefig(name + '_hist_all_percentage.png')
    plt.close()
    
    #by region
#    results_region = pd.merge(X['Region'],rating_sum, right_index=True, left_index=True)
#    results_region = results_region.groupby(['Region', 'Rating']).size().to_frame('Count').reset_index()

#    region_1 = results_region[results_region['Region'] =='West'].copy()
#    region_1 = region_1[['Rating', 'Count']]
#    region_1.columns = ['Rating', 'West']

#    region_2 = results_region[results_region['Region'] =='South'].copy()
#    region_2 = region_2[['Rating', 'Count']]
#    region_2.columns = ['Rating', 'South']
    
#    region_3 = results_region[results_region['Region'] =='MidWest'].copy()
#    region_3 = region_3[['Rating', 'Count']]
#    region_3.columns = ['Rating', 'MidWest']

#    region_4 = results_region[results_region['Region'] =='NorthEast'].copy()
#    region_4 = region_4[['Rating', 'Count']]
#    region_4.columns = ['Rating', 'NorthEast']
    
#    region = pd.DataFrame(mapping['Rating'])
#    region['West'] = region.Rating.map(region_1.set_index('Rating')['West']).fillna(0)
#    region['South'] = region.Rating.map(region_2.set_index('Rating')['South']).fillna(0)
#    region['MidWest'] = region.Rating.map(region_3.set_index('Rating')['MidWest']).fillna(0)
#    region['NorthEast'] = region.Rating.map(region_4.set_index('Rating')['NorthEast']).fillna(0)
    
#    region.index = region['Rating']
#    plot_region_count = region.plot.bar()
#    plot_region_count.figure.savefig(name +'_region_count.png')
    
#    region_per = region.copy()
#    region_per['West'] = region['West'].transform(lambda x: x/sum(x))
#    region_per['South'] = region['South'].transform(lambda x: x/sum(x))
#    region_per['MidWest'] = region['MidWest'].transform(lambda x: x/sum(x))
#    region_per['NorthEast'] = region['NorthEast'].transform(lambda x: x/sum(x))
    
#    plot_region_per = region_per.plot.bar()
#    plot_region_per.figure.savefig(name +'_region_percentage.png')
    
# calculate rating for X_train and save csv
#get the variables to have in the output file
id = X_train[["dosname", "masterloanidtrepp", "maturitydate", "observation_date"]]
pd.merge(id, get_score(X_train, mapping),right_index=True, left_index=True).to_csv(os.path.join(model_path, 'rating_train.csv'), index=False)

plot_data(X_train, mapping, "5_1_4_score/output/train")

id = X_test[["dosname", "masterloanidtrepp", "maturitydate", "observation_date"]]
pd.merge(id, get_score(X_test, mapping),right_index=True, left_index=True).to_csv(os.path.join(model_path, 'rating_test.csv'), index=False)

plot_data(X_test, mapping, "5_1_4_score/output/test")
#create a box plot for all data