import os
import sys
import yaml
import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype
import scipy.stats.stats as stats

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

# create output path
os.makedirs(output_path, exist_ok=True)

# create output path
reports_path = os.path.join('5_1_2_information_value/output')
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
del X_train, y_train # free up memory
df_test = pd.concat([X_test, y_test], axis=1, sort=False)
del X_test, y_test # free up memory
df_raw = pd.concat([df_train, df_test], axis=0, sort=False)
del df_test # free up memory

##########################
## Categorical features ##
##########################

# Division
map_division = {
    'MidWest-EastNorthCentral':-0.299697847673694,
    'MidWest-WestNorthCentral':-0.0566016068284879,
    'NorthEast-MiddleAtlantic':0.402240909366983,
    'NorthEast-NewEngland':0.683402128375227,
    'Other':-0.428183629650907,
    'South-Atlantic':-0.0581048272887034,
    'South-EastSouthCentral':-0.448487871529508,
    'South-WestSouthCentral':0.0634321800879977,
    'West-Mountain':-0.407828042623753,
    'West-Pacific':0.431752267434479,
}
df_raw['Division_transformed'] = df_raw['Division'].map(map_division)

# interestonly
map_interestonly = {
    'N':0.355233900359136,
    'P':-1.55189530376839,
    'Y':-0.183805615884891,
}
df_raw['interestonly_transformed'] = df_raw['interestonly'].map(map_interestonly)


########################
## Numerical features ##
########################

# priorfydscrncf
df_raw['priorfydscr_transformed'] = pd.cut(
    df_raw['priorfydscr'],
    bins=[-np.inf, 1.16, 1.33, 1.44, 1.7, np.inf],
    labels=[-1.42116906348379, -0.198988839341774, 0.314881941030989, 0.67442606502331, 1.52887902911955],
    right=True,
)
df_raw['priorfydscr_transformed'] = np.where(np.isnan(df_raw['priorfydscr']), 0.496240514681718, df_raw['priorfydscr_transformed'])

# mrfytdocc
df_raw['mrfytdocc_transformed'] = pd.cut(
    df_raw['mrfytdocc'],
    bins=[-np.inf, 87, 92, np.inf],
    labels=[-1.33857870836316, -0.263308549115889, 0.591996118131294],
    right=True,
)
df_raw['mrfytdocc_transformed'] = np.where(np.isnan(df_raw['mrfytdocc']), 0.136420492995575, df_raw['mrfytdocc_transformed'])

# debt_yield_p1
df_raw['debt_yield_p1_transformed'] = pd.cut(
    df_raw['debt_yield_p1'],
    bins=[-np.inf, 2.8386262467, 5.9510906194, 8.3319934966, 10.316174631, 11.606564857, 14.840957634, np.inf],
    labels=[-1.21375140103703, -0.751055042751868, -0.452148192770352, -0.12528327272148, 0.304915172400912, 0.83610946675043, 1.37096446576086],
    right=True,
)
df_raw['debt_yield_p1_transformed'] = np.where(np.isnan(df_raw['debt_yield_p1']), 0.546897381049544, df_raw['debt_yield_p1_transformed'])

# priorfyocc
df_raw['priorfyocc_transformed'] = pd.cut(
    df_raw['priorfyocc'],
    bins=[-np.inf, 88, 93, 97.34, np.inf],
    labels=[-1.20796457184999, -0.268470622317306, 0.222474218671472, 0.547173823606788],
    right=True,
)
df_raw['priorfyocc_transformed'] = np.where(np.isnan(df_raw['priorfyocc']), 0.363608045979996, df_raw['priorfyocc_transformed'])

# OLTV
df_raw['OLTV_transformed'] = pd.cut(
    df_raw['OLTV'],
    bins=[-np.inf, 55.9, 63.22, 75.3, np.inf],
    labels=[1.14776888856407, 0.338983927057472, 0.0624579494529431, -0.363398346745822],
    right=True,
)
df_raw['OLTV_transformed'] = np.where(np.isnan(df_raw['OLTV']), 0.0971615242761209, df_raw['OLTV_transformed'])


##################################################################
## Automatic fine-class binning and initial univariate analysis ##
##################################################################

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
        df_temp.to_excel(excel_writer, variable)
        df_raw[variable+'_transformed'] = pd.cut(df_raw[variable], bins=bins, labels=pd.Series(df_temp['WoE'].values.tolist()[1:]).fillna(0).tolist())
        df_raw[variable+'_transformed'] = np.where(np.isnan(df_raw[variable]), df_temp['WoE'].values.tolist()[0], df_raw[variable+'_transformed'])
    elif variable in categorical_columns_as_features:
        IV_total, df_temp, bins = run_fine_classing(df_train[[variable, bad_flag]], variable, n)
        df_temp.to_excel(excel_writer, variable)
        df_raw[variable].fillna('missing', inplace=True)
        df_raw[variable+'_transformed'] = df_raw[variable].map(bins)
    df_raw[variable+'_transformed'].fillna(0, inplace=True)
    
    # Store total IV
    dict_IV[variable] = IV_total

# Save the excel file
excel_writer.save()

# Output total IV
df_IV = pd.DataFrame.from_dict(dict_IV, orient='index', columns=['IV_total'])
df_IV = df_IV.sort_values(by='IV_total', ascending=False)
print(df_IV)
#excel_writer = pd.ExcelWriter(os.path.join(reports_path, 'information-value.xlsx'))
#df_IV.to_excel(excel_writer, variable)
#excel_writer.save()

#Saving JSON file
# Data Representation
df_IV.reset_index(inplace=True)
df_IV = df_IV.rename(columns={"index": "Feature"})

df_IV.to_json(os.path.join(reports_path, 'information-value.json'), orient="records")


# Split back into train and test
X_train = df_raw.loc[df_raw['label']=='train']
X_test = df_raw.loc[df_raw['label']=='test']

# Save data
X_train.to_csv(os.path.join(output_path, 'X_train_transformed.csv'), index=False)
X_test.to_csv(os.path.join(output_path, 'X_test_transformed.csv'), index=False)
