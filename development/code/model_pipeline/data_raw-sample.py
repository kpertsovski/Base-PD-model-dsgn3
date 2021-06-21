# import the required libraries
import os
import sys
import yaml
import xlsxwriter
import pandas as pd

# read from command line
data_path = sys.argv[1]
output_path = sys.argv[2]

# create output path
os.makedirs(output_path, exist_ok=True)

# load size parameter for length of sample dataset
params = yaml.safe_load(open('params.yaml'))['data_raw']
size_cutoff = params['size_cutoff']

# self declared datatypes:
dict_datatypes = {'masterloanidtrepp':'int64', 'observation_date':'object'}

# alternative by inference from small sample:
df_raw = pd.read_csv(os.path.join(data_path, 'TREPP_full-dataset.csv'), nrows=2*size_cutoff, dtype=dict_datatypes, low_memory=False)

# merge to obtain 'CLTV_1' and 'debt_yield_p1'
df_temp = pd.read_csv(os.path.join(data_path, 'improved_debt_yield_cltv.csv'), dtype=dict_datatypes)
df_raw = df_raw.merge(
    df_temp[['masterloanidtrepp','observation_date','CLTV_1','debt_yield_p1']],
    how='left',
    on=['masterloanidtrepp','observation_date']
)

# free up memory
del df_temp

# take certain length of full dataset as sample
if size_cutoff<0:
    df_sample = df_raw
else:
    df_sample = df_raw.sample(n=min(len(df_raw),size_cutoff), random_state=7)
    del df_raw # free up memory

# save sample dataset
df_sample.to_csv(os.path.join(output_path, 'TREPP_sample-dataset.csv'))

# Excel file for user input on which fields to test for data quality
#user_input_folder = os.path.join('data','00_user_input')
#os.makedirs(user_input_folder, exist_ok=True)

#df_user_input = pd.DataFrame(df_sample.columns.tolist(), columns=['Variables'])
#df_user_input['dq_check'] = 'yes'
#df_user_input.to_excel(os.path.join(user_input_folder, 'dq_checks.xlsx'))

#workbook = xlsxwriter.Workbook(os.path.join(user_input_folder, 'dq_checks.xlsx'))
#worksheet = workbook.add_worksheet()

#worksheet.write('A1', 'Variable')
#worksheet.write('B1', 'dq_check')
#for i in range(len(df_sample.columns.tolist())):
#    worksheet.write('A'+str(i+2), df_sample.columns.tolist()[i])
#    worksheet.write('B'+str(i+2), 'yes')
#    worksheet.data_validation('B'+str(i+2), {
#        'validate': 'list',
#        'source': ['yes', 'no']
#    })
#
#workbook.close()