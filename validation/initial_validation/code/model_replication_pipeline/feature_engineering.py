import os
import re
import sys
import yaml
import json
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from pandas.api.types import is_string_dtype
import scipy.stats.stats as stats
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score, roc_curve

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

# create output path
os.makedirs(output_path, exist_ok=True)

# create output path
reports_path = os.path.join('5_1_2_univariate_analysis', 'output')
os.makedirs(reports_path, exist_ok=True)
excel_writer = pd.ExcelWriter(os.path.join(reports_path, 'mapping_value-to-WoE.xlsx'))

# load fine classing number of bins
params = yaml.safe_load(open('params.yaml'))['feature_engineering']
n_bins = params['n_bins_fine_classing']

# load independent variables
params = yaml.safe_load(open('params.yaml'))['model_development']
numerical_columns_as_features = params['numerical_columns_as_features']
categorical_columns_as_features = params['categorical_columns_as_features']

# load dependent variable
params = yaml.safe_load(open('params.yaml'))['sampling']
bad_flag = params['bad_flag']

# import dependent variables
y_train = pd.read_csv(os.path.join(data_path, 'y_train.csv'))
y_test = pd.read_csv(os.path.join(data_path, 'y_test.csv'))
y_train.to_csv(os.path.join(output_path, 'y_train_transformed.csv'), index=False) # no transformation
y_test.to_csv(os.path.join(output_path, 'y_test_transformed.csv'), index=False) # no transformation

# import independent variables
X_train = pd.read_csv(os.path.join(data_path, 'X_train.csv'))
X_test = pd.read_csv(os.path.join(data_path, 'X_test.csv'))

# recreate entire dataframe
df_train = pd.concat([X_train, y_train], axis=1, sort=False)
df_test = pd.concat([X_test, y_test], axis=1, sort=False)
del X_test, y_test # free up memory
df_raw = pd.concat([df_train, df_test], axis=0, sort=False)
del df_test # free up memory


#################################################################
## Automatic fine-class binning and information value analysis ##
#################################################################

def run_fine_classing(df, variable, n_bins=n_bins):
    if(is_string_dtype(df[variable])):
        df['bin_range'] = df[variable]
        df['bin_range'] = df['bin_range'].astype('category')
        df['bin_range'] = df['bin_range'].cat.add_categories('missing')
    else:
        df.sort_values(by=[variable,bad_flag], na_position='last', inplace=True)
        df_temp = df.dropna(subset=[variable])
        df_temp['goods_cumsum'] = (1-df_temp[bad_flag]).cumsum()
        df_temp['bins_temp'] = pd.qcut(df_temp['goods_cumsum'], q=min(n_bins, df_temp['goods_cumsum'].nunique()), duplicates='drop')
        bins = list(dict.fromkeys(df_temp.groupby('bins_temp')[variable].min().tolist() + [df_temp[variable].max()]))
        df['bin_range'] = pd.cut(df[variable], bins, duplicates='drop')
        df['bin_range'] = df['bin_range'].cat.add_categories('missing')
    df['bin_range'].fillna('missing', inplace=True)
    df_return = pd.DataFrame(index=df['bin_range'].cat.categories)
    df_bads = df.groupby('bin_range').agg({bad_flag: lambda x: (x==1).sum()}).rename(columns={bad_flag: 'Bads'})
    df_return = pd.merge(df_return, df_bads, how='left', left_index=True, right_index=True)
    df_goods = df.groupby('bin_range').agg({bad_flag: lambda x: (x==0).sum()}).rename(columns={bad_flag: 'Goods'})
    df_return = pd.merge(df_return, df_goods, how='left', left_index=True, right_index=True)
    df_return['pct_Bads'] = df_return['Bads'] / df_return['Bads'].sum()
    df_return['pct_Goods'] = df_return['Goods'] / df_return['Goods'].sum()
    df_return['WoE'] = df_return.apply(lambda x: np.log(x['pct_Goods']/x['pct_Bads']), axis=1)
    df_return['IV'] = df_return.apply(lambda x: (x['pct_Goods']-x['pct_Bads'])*x['WoE'], axis=1)
    
    df_return = df_return.replace([np.inf, -np.inf], np.nan)
    
    df_return = df_return.reset_index().rename(columns={'index':'bin_range'})
    df_return = df_return.apply(np.roll, shift=1)
    
    IV_total = df_return['IV'].sum()
    
    if(is_string_dtype(df[variable])):
        bins_temp = df_return[['bin_range','WoE']].drop_duplicates()
        bins = pd.Series(bins_temp['WoE'].values, index=bins_temp['bin_range']).to_dict()
    
    return IV_total, df_return, bins

# Run fine classing
dict_IV = {}
for variable in numerical_columns_as_features+categorical_columns_as_features:
    if variable in numerical_columns_as_features:
        r = 0
        n = n_bins
        condition = True
        while condition:
            IV_total, df_temp, bins = run_fine_classing(df_train[[variable, bad_flag]], variable, n)
            r, p = stats.spearmanr(df_temp.index.values[1:], df_temp['WoE'].values[1:])
            n = n-1
            condition = True if ((n>1) and ((np.abs(r) < 1)) or np.isnan(r)) else False
        df_temp.to_excel(excel_writer, re.sub(r"[\[:]", "_", variable))
        df_raw[variable+'_transformed'] = pd.cut(df_raw[variable], bins=bins, labels=pd.Series(df_temp['WoE'].values.tolist()[1:]).fillna(0).tolist())
        df_raw[variable+'_transformed'] = np.where(np.isnan(df_raw[variable]), df_temp['WoE'].values.tolist()[0], df_raw[variable+'_transformed'])
    elif variable in categorical_columns_as_features:
        IV_total, df_temp, bins = run_fine_classing(df_train[[variable, bad_flag]], variable, n)
        df_temp.to_excel(excel_writer, re.sub(r"[\[:]", "_", variable))
        df_raw[variable].fillna('missing', inplace=True)
        df_raw[variable+'_transformed'] = df_raw[variable].map(bins)
    df_raw[variable+'_transformed'].fillna(0, inplace=True)
    
    # Store total IV
    dict_IV[variable] = IV_total

# Save the excel file
excel_writer.save()

# Output total IV
df_IV = pd.DataFrame.from_dict(dict_IV, orient='index', columns=['IV_total'])
df_IV = df_IV.sort_values(by='IV_total', ascending=False).rename_axis('Parameter').reset_index()
print(df_IV)
df_IV.to_csv(os.path.join(reports_path, 'information-value.csv'))


####################################################################
## Automatic univariate analysis and Gini coefficient calculation ##
####################################################################

excel_writer = pd.ExcelWriter(os.path.join(reports_path, 'univariate-analysis_model-coefficients.xlsx'))
dict_gini = {}
df_total = pd.DataFrame()
for variable in numerical_columns_as_features+categorical_columns_as_features:
    X = df_raw.loc[df_raw['label']=='train', variable+'_transformed']
    y = y_train
    logit_model = sm.Logit(y, X)
    results = logit_model.fit()
    df_results = results.summary2().tables[1]
    df_results = df_results.rename_axis('Parameter').reset_index()
    df_results.to_excel(excel_writer, variable)
    df_total = df_total.append(df_results)
    
    # Area Under the Curve (AUC) and Gini coefficient
    auc = roc_auc_score(y, results.predict(X))
    gini = 2*auc - 1
    # Gini coefficient
    dict_gini[variable] = gini
excel_writer.save()

df_total['Parameter'] = df_total['Parameter'].str.replace(r'_transformed', '')

# Output Gini coefficients
df_gini = pd.DataFrame.from_dict(dict_gini, orient='index', columns=['Gini coefficient'])
df_gini = df_gini.sort_values(by='Gini coefficient', ascending=False).rename_axis('Parameter').reset_index()
df_gini['Gini coefficient'] = df_gini['Gini coefficient'].round(decimals=3)
df_gini.to_csv(os.path.join(reports_path, 'univariate-analysis_gini-coefficients.csv'))
df_gini.to_json(os.path.join(reports_path, 'univariate-analysis_gini-coefficients.json'), orient='records')

df_merged = pd.merge(df_total[['Parameter','Coef.','P>|z|']], df_gini, how='left', on='Parameter')
print(df_merged)
df_merged.to_csv(os.path.join(reports_path, 'univariate-analysis.csv'))
df_merged.to_json(os.path.join(reports_path, 'univariate-analysis.json'), orient='records')

# Split back into train and test
X_train = df_raw.loc[df_raw['label']=='train']
X_test = df_raw.loc[df_raw['label']=='test']

# Save data
X_train.to_csv(os.path.join(output_path, 'X_train_transformed.csv'), index=False)
X_test.to_csv(os.path.join(output_path, 'X_test_transformed.csv'), index=False)