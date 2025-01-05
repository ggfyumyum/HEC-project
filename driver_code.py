import os
import pandas as pd
import numpy as np
import seaborn as sns

from data_validation import Validator
from data_analysisv2 import Processor
from data_vizualisation import Viz
from eq5d_profile1 import eq5dvalue
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

#create a dictionary with each group having its own dataframe
#you need to specify which column the group label is
group_col = 'TIME_INTERVAL'
siloed_data = Processor(data,group_col).siloed_data

paretian = Processor(data,group_col).paretian('Preop','Postop')
t10_index = Processor(data,group_col).top_frequency()
ts_delta_binary = Processor(data,group_col).ts_binary()
data_with_util = eq5dvalue(data, value_set,'NewZealand').calculate_util()
util_ranking = eq5dvalue(data, value_set,'NewZealand').create_util_ranking()
hpg_data = Processor(data,group_col).hpg(paretian,util_ranking)

Viz(hpg_data).hpg()

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
#print(util_test_nz)
#print(t10_index)

print('done')
