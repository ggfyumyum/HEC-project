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
decrement_table = pd.read_excel('VS_decrements.xlsx')

#if there is a valueset available, use it. Otherwise, use the decrement table to generate a fresh one.
if os.path.exists('valueset_data.csv'):
    value_set = pd.read_csv('valueset_data.csv')
else:
    value_set = decrement_processing(decrement_table).generate_value_set()
    decrement_processing.export_value_set(value_set)

#run the raw data through the validator
data = Validator(raw_data).data
#append the utility scores and calculation to the original data
data = eq5dvalue(data, value_set,'NewZealand').calculate_util()

#create a dictionary with each group having its own dataframe, store it in siloed_data
group_col = 'TIME_INTERVAL'
group1 = 'Preop'
group2 = 'Postop'
siloed_data = Processor(data,group_col).siloed_data

#******************************************* DATA ANALYSIS *****************************************************

#create some new DFs which can be used for plotting or printed directly for analysis
t10_index = Processor(data,group_col).top_frequency()
ts_delta_binary = Processor(data,group_col).ts_binary()
paretian = Processor(data,group_col).paretian(group1,group2)
data_LSS = Processor(data,group_col).level_frequency_score()

#print(paretian)
#print(t10_index)
#print(ts_delta_binary)
#print(t10_index)

#print a simple descripton for each group and a binary format description
def show_desc(siloed_data):
    #input = a dictionary
    for group_name, group_data in siloed_data.items():
        simple = Processor(group_data).simple_desc()
        binary = Processor(group_data).binary_desc()
        print('*' * 100)
        print(group_name + ' group')
        print(simple)
        print(binary)
    return

show_desc(siloed_data)

#*************************** PLOTTING FUNCTIONS **********************************************

#histogram of the dimension scores from the whole dataset
as_pct = Processor(data).get_percent()
Viz(as_pct).histogram()

#side-by-side histograms comparing groups
grouped_pct = {}
for key, item in siloed_data.items():
    grouped_pct[key] = Processor(item).get_percent()
Viz(grouped_pct).histogram_by_group()

#health profile grid, requires the paretian dataframe
Viz(Processor(data,group_col).hpg(paretian,group1,group2)).hpg()

#time series of the binary score change
Viz(ts_delta_binary).ts()

print('done')
