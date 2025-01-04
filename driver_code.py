import pandas as pd
import numpy as np
import seaborn as sns

from data_validation import Validator
from data_analysisv2 import Processor
from data_vizualisation import Viz
from eq5d_profile1 import eq5dvalue

print('RUNNING')

raw_data = pd.read_csv('fake_data.csv')
dec = pd.read_excel('VS_decrements.xlsx')

#run the data through the validator
data = Validator(raw_data).data

#create a dictionary with each group having its own dataframe
#you need to specify which column the group label is
group_col = 'TIME_INTERVAL'
siloed_data = Processor(data,group_col).siloed_data

x = Processor(data,group_col)

#run paretian analysis
paretian = Processor(data,group_col).paretian('Preop','Postop')
print(paretian)

print(Processor(data,group_col).frequency())

'''
#print a simple descripton for each group and a binary format description
#todo cumulative analysis
for group_name, group_data in siloed_data.items():
    simple = Processor(group_data).simple_desc()
    binary = Processor(group_data).binary_desc()
    print('*' * 100)
    print(group_name + ' group')
    print(simple)
    print(binary)

#print a time series plot of binary data
ts_delta_binary = Processor(data,group_col).ts_binary()
Viz(ts_delta_binary).ts()
'''

#calcukate utility value for an NZ sample
result = eq5dvalue(data, dec,'NewZealand').calculate_util()
print(result)



print('done')
