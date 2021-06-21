# import the required libraries
import os
import sys
import yaml
import pandas as pd
from datetime import datetime

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

# create output path
os.makedirs(output_path, exist_ok=True)

# load term-default cutoff parameter (months)
params = yaml.safe_load(open('params.yaml'))['data_clean']
term_default_cutoff = params['term_default_cutoff']

# import data
temp = pd.read_csv(os.path.join(data_path, 'TREPP_sample-dataset.csv'), iterator=True, low_memory=False, chunksize=100000)
df_raw = pd.concat(temp, ignore_index=True)

# free up memory
del temp

# remove empty columns
df_raw = df_raw.dropna(how='all', axis=1)

# remove loans with maturity date less than x (e.g. 12) months from observation date
df_raw.dropna(subset=['maturitydate', 'observation_date'], inplace=True)
df_raw['maturitydate'] = df_raw['maturitydate'].apply(lambda x: datetime.strptime(('%f' % x).rstrip('0').rstrip('.'), '%Y%m%d'))
df_raw['observation_date'] = df_raw['observation_date'].apply(lambda x: datetime.strptime(x, '%Y_%m'))
df_raw['TTM_months'] = (df_raw['maturitydate'].dt.year - df_raw['observation_date'].dt.year) * 12 + (df_raw['maturitydate'].dt.month - df_raw['observation_date'].dt.month)

# print(df_raw[['observation_date','maturitydate','TTM_months']].head())

df_clean = df_raw[df_raw['TTM_months'] > term_default_cutoff]
print('Reduction in dataframe size after term-to-maturity cutoff: {size1} -> {size2}'.format(size1=len(df_raw), size2=len(df_clean)))

# save sample dataset
df_clean.to_csv(os.path.join(output_path, 'TREPP_sample-dataset_term-defaults.csv'))