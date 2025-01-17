import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer
from eq5d_profile import Eq5dvalue
from eq5d_decrement_processing import Decrement_processing

print('RUNNING')

#Required raw inputs
raw_data = pd.read_csv('knee_data.csv')
decrement_table = pd.read_excel('VS_decrements.xlsx')
multiple_groups = True
group_col = 'TIME_INTERVAL'
country = 'NewZealand'

filter = False

#if there is a valueset available, use it. Otherwise, use the decrement table to generate a fresh one.
if os.path.exists('valueset_data.csv'):
    value_set = pd.read_csv('valueset_data.csv')
else:
    value_set = Decrement_processing(decrement_table).generate_value_set()
    Decrement_processing.export_value_set(value_set)

if filter:
    #filter the data by filter if needed
    raw_data = Validator.apply_filter(raw_data)
    #only see the male group
    raw_data = Validator.apply_filter(raw_data,group='GENDER',subset='M')

#run the raw data through the validator
validated_data = Validator(raw_data,multiple_groups,group_col)

data = validated_data.data
group_list = validated_data.group_list

#append the utility scores and ranked calculations to the original data
data_with_util = Eq5dvalue(data, value_set,country).calculate_util()

#create a dictionary with each group having its own dataframe, store it in siloed_data
siloed_data = Processor(data,group_list,group_col).siloed_data

#******************************************* DATA ANALYSIS *****************************************************
#create some new DFs which can be used for plotting or printed directly for analysis

t10_index = Processor(data,group_list,group_col).top_frequency()
ts_delta_binary = Processor(data,group_list,group_col).ts_binary()
paretian = Processor(data,group_list,group_col).paretian()
data_LSS = Processor(data,group_list,group_col).level_frequency_score()
avg_utility = Processor(data,group_list,group_col).ts_utility()
avg_eqvas = Processor(data,group_list,group_col).ts_eqvas()
hdsc = Processor(data,group_list,group_col).health_state_density_curve()


print(paretian)
print(t10_index)
print(ts_delta_binary)
print(data_LSS)
print(avg_utility)
print(avg_eqvas)

#print a simple descripton for each group and a binary format description
def show_desc(siloed_data):
    #input = a dictionary
    for group_name, group_data in siloed_data.items():
        simple = Processor(group_data).simple_desc()
        binary = Processor(group_data).binary_desc()
        print('*' * 100)
        print(group_name, 'group')
        print(simple)
        print(binary)
    return

show_desc(siloed_data)

#*************************** PLOTTING FUNCTIONS **********************************************

#histogram of the dimension scores from the whole dataset
as_pct = Processor(data).get_percent()
Visualizer(as_pct).histogram()

#side-by-side histograms comparing groups
grouped_pct = {}
for key, item in siloed_data.items():
    grouped_pct[key] = Processor(item).get_percent()
Visualizer(grouped_pct).histogram_by_group()

#health profile grid, requires the paretian dataframe
if len(group_list)==2:
    Visualizer(Processor(data,group_list,group_col).hpg(paretian,group_list[0],group_list[1])).hpg()

#avg util
Visualizer(avg_utility).time_series()

#eqvas
Visualizer(avg_eqvas).time_series()

#hdsc
Visualizer(hdsc).health_state_density_curve()


#data = Processor(data_with_util,group_list,group_col).utility_density()

#Visualizer(data).utility_density()

plt.show()

print('done')





