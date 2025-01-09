import os
import pandas as pd
import numpy as np
import seaborn as sns

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Viz
from eq5d_profile import eq5dvalue
from eq5d_decrement_processing import decrement_processing

print('RUNNING')

raw_data = pd.read_csv('fake_data.csv')
dec = pd.read_excel('VS_decrements.xlsx')

if os.path.exists('valueset_data.csv'):
    value_set = pd.read_csv('valueset_data.csv')
else:
    value_set = decrement_processing(dec).generate_value_set()
    decrement_processing.export_value_set(value_set)

#run the data through the validator
data = Validator(raw_data).data
print('data before',data)
#append the utility scores and calculation to the original data
data = eq5dvalue(data, value_set,'NewZealand')
data = data.calculate_util()
print('the data after',data)
#data.to_csv('data_output.csv')

#create a dictionary with each group having its own dataframe, specify which column the group label is
group_col = 'TIME_INTERVAL'
group1 = 'Preop'
group2 = 'Postop'
siloed_data = Processor(data,group_col).siloed_data
t10_index = Processor(data,group_col).top_frequency()
ts_delta_binary = Processor(data,group_col).ts_binary()
paretian = Processor(data,group_col).paretian(group1,group2)

data = Processor(data,group_col).level_sum_score()
print(data)

Viz(data).lss_utility()
#Viz(Processor(data,group_col).hpg(paretian,group1,group2)).hpg()


#print a simple descripton for each group and a binary format description
def show_desc(data):
    #input = a dictionary of siloed data
    for group_name, group_data in data.items():
        simple = Processor(group_data).simple_desc()
        binary = Processor(group_data).binary_desc()
        print('*' * 100)
        print(group_name + ' group')
        print(simple)
        print(binary)
    return

#show_desc(siloed_data)
#Viz(ts_delta_binary).ts()
#print(paretian)
#print(t10_index)
#print(ts_delta_binary)
#print(t10_index)

print('done')
