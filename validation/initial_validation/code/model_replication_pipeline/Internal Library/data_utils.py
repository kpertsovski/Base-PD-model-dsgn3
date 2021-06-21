# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 12:49:52 2020

@author: Jun Peng
"""

# Analytics libraries (public)
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from numpy import mean
from numpy import std
from pylab import rcParams


def missing_value_statistic(df):
    """
    Function to summarize missing value statistic.
    @param df: pandas dataframe object
    @return: missing summary statistics for all variable with missing values
    """
    ms = (df.isnull().sum()/len(df) * 100.0)
    df_missing = pd.DataFrame({"Feature":list(df), "% Missing": ms.values})
    df_missing = df_missing.sort_values(by="% Missing", ascending=False)
    df_missing = df_missing.reset_index()
    df_missing = df_missing.drop(columns = ["index"])
    df_missing_fn = df_missing[df_missing["% Missing"] > 0]
    return(df_missing_fn)

 
# Input should be a dataframe object, threshold should be in decimals, e.g., for threshold of 25%, enter 0.25
# Output is the final dataset after removing the features with higher missing value % than the threshold; Output is in form of dataframe
def remove_missing(df, threshold):
    """
    Function to remove the features with missing values above the threshold
    @param df: pandas dataframe object
    @param threshold: in decimals
    @return: the dataframe after missing columns are removed
    """
    ms = (df.isnull().sum()/len(df) * 100.0)
    df_missing = pd.DataFrame({"Feature":list(df), "% Missing": ms.values})
    df_1 = df_missing[df_missing["% Missing"]< (threshold*100.0)]
    feat_list = list(df_1["Feature"])
    df_out = df[feat_list]
    return(df_out)

# drop missing if % missing is less than 5%
def drop_missing_obs(df, threshold):
    """
    Function to drop missing observations below certain threshold
    @param df: pandas dataframe object
    @param threshold: in decimals
    @return: the dataframe after missing observations are removed
    """
    df_missing=missing_value_statistic(df)
    df_temp=df_missing[df_missing["% Missing"]< (threshold*100.0)]
    feat_list=list(df_temp['Feature'])
    df_out=df.dropna(subset=feat_list)
    return(df_out)

# Function to seperate lists for numeric and non-numeric features
# The input of this function of the dataset in form of dataframe
# It outputs a list of two elements(lists)
# element #1 is a list of numerical features in the data set
# element #2 is a list of categorical features in the data set
def data_types(df):
    """
    Function to separate list for numeric and  non-numeric features
    @param df: pandas dataframe object
    @return: list of numeric and non-numeric features
    """
    numeric = []
    categorical = []
    for i in list(df):
        if (df[i].dtype== np.int64) | (df[i].dtype== np.float64):
            numeric.append(i)
        else:
            categorical.append(i)
    return [numeric, categorical]

# Function to create box plots for variables
def plot_box_var(df, col_name):
    """
    Function to visualize a variable in a dataframe.
    @param df: pandas dataframe object
    @param col_name: variable name in the given dataframe
    
    """
    f, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12,3), dpi=90)
    
    # Plot without loan status
    sns.distplot(df.loc[df[col_name].notnull(), col_name], kde=False, ax=ax1)

    ax1.set_xlabel(col_name)
    ax1.set_ylabel('Count')
    ax1.set_title(col_name)

    # Plot box plots
    sns.boxplot(x=col_name, data=df, ax=ax2)
    ax2.set_ylabel('')
    ax2.set_title(col_name)      
    ax2.set_xlabel(col_name)
    
    plt.tight_layout()

# Function to visualize both continuous and discrete variables
def plot_var(df, col_name, full_name, default_flag, default_flag_value, continuous):
    """
    Function to visualize a variable in a dataframe.
    @param df: pandas dataframe object
    @param col_name: variable name in the given dataframe
    @param full_name: full variable name to be printed on the graph
    @param continuous: True if the variable is continuous, False otherwise
    """
    f, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(12,3), dpi=90)
    
    # Plot without loan status
    if continuous:
        sns.distplot(df.loc[df[col_name].notnull(), col_name], kde=False, ax=ax1)
    else:
        sns.countplot(df[col_name], order=sorted(df[col_name].unique()), color='#5975A4', saturation=1, ax=ax1)
    ax1.set_xlabel(full_name)
    ax1.set_ylabel('Count')
    ax1.set_title(full_name)

    # Plot with loan status
    if continuous:
        sns.boxplot(x=col_name, y=default_flag, data=df, ax=ax2)
        ax2.set_ylabel('')
        ax2.set_title(full_name + ' by Loan Status')
    else:
        charge_off_rates = df.groupby(col_name)[default_flag].value_counts(normalize=True).loc[:,default_flag_value]
        sns.barplot(x=charge_off_rates.index, y=charge_off_rates.values, color='#5975A4', saturation=1, ax=ax2)
        ax2.set_ylabel('Fraction of df Charged-off')
        ax2.set_title('Charge-off Rate by ' + full_name)
    ax2.set_xlabel(full_name)
    
    plt.tight_layout()

# Function to detect outliers
# Inputs is dataset in question and cut-off considered is 3 standard deviations
# Outputs are percentage of outliers for each variable
def outliers_detection(df):  
    """
    Function to detect outliers 3 standard deviations away
    @param df: pandas dataframe object
    @return: percentgage outliers for each variable
    """
    data_mean, data_std = mean(df), std(df) 
    cut_off = data_std * 3  
    lower, upper = data_mean - cut_off, data_mean + cut_off
    outliers = len([x for x in df if x < lower or x > upper])/len(df)*100
    return ("Percentage of outliers: %.2f%% " % (outliers))


# Inputs is dataset in question, numerical features and threshold 
# dataset should be provided in form of pandas dataframe
# numerical features should be provided as a list of numerical feature namesprovided as a list of numerical feature names
# threshold should be provided in form of percentage. e.g., 10.0 means top and bottom 10 percentile are considered as outliers
def outlier_treatment(df, num_feat,threshold):
    """
    Function to treats outliers, cap outliers at percentile threshold
    @param df: pandas dataframe object
    @param num_feat: list of numerical feature names
    @param threshold: percentile threshold 
    @return: the treated dataframe
    """
    for col in df[num_feat].columns:
        percentiles = df[col].quantile([threshold/100.0,(100.0-threshold)/100.0]).values
        df[col][df[col] < percentiles[0]] = percentiles[0]
        df[col][df[col] > percentiles[1]] = percentiles[1]
    return (df)


# Function to compare numeric feature distributions
# Inputs are two datasets in question and all features as list object
# Optional inputs are dataframe names to be used a label in the plot
# Outputs are histogram plots comparing two datasets
def compare_distribution(df1, df2, features, df1_name="Training", df2_name="Test"):
    """
    Function to treats outliers, cap outliers at percentile threshold
    @param df1: pandas dataframe object
    @param df2: pandas dataframe object
    @param features: list of features for which distribution need to be compared
    @param df1_name: Name of the first dataframe
    @param df2_name: Name of the second dataframe
    """
    for i in features:
        rcParams['figure.figsize'] = 7, 5
        p1=sns.kdeplot(df1[i], label= " ".join([i, df1_name]), shade=True, color="r")
        p1=sns.kdeplot(df2[i], label= " ".join([i, df2_name]), shade=True, color="b")
        plt.legend()
        plt.show()

# Function to compare non-numeric feature frequency
# Inputs are two datasets in question and all features as list object
# Optional inputs are dataframe names to be used a label in the plot
# Frequency outputs are printed on the screen
def compare_frequency(df1, df2, features, df1_name="Training", df2_name="Test"):
    """
    Function to treats outliers, cap outliers at percentile threshold
    @param df1: pandas dataframe object
    @param df2: pandas dataframe object
    @param features: list of features for which frequency need to be compared
    @param df1_name: Name of the first dataframe
    @param df2_name: Name of the second dataframe
    """
    for i in features:
        var_summary_1 = df1[i].value_counts(normalize=True)
        var_summary_2 = df2[i].value_counts(normalize=True)
        print("---------------------------------------")
        print(i)
        print("---------------------------------------")
        print(pd.DataFrame({df1_name: var_summary_1, df2_name: var_summary_2}).sort_index())

