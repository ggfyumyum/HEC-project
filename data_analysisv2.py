import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#the functions in this class accept raw dataframe, and extract some type of statistics/analysis
#the functions return dataframes which directly show summary statistics, or which can be sent to vizualisation

class Processor:

    def __init__(self, data, group_col='Default'):

        #The processor can accept two types of data, one type is the entire dataset. The other is a dataset containing a single group, for example only pre-op patients. 
        #If group col not specified, assume the latter
        self.df = pd.DataFrame(data)
        self.group_col = group_col

        #If there are multiple groups, split the data into dataframes with one group each
        if group_col!='Default':
            self.siloed_data = {group: data for group, data in self.df.groupby(self.group_col)}
        
        else:
        #If the dataset passed is a single group, do some modification to assist for later single-group analysis.
            self.trim_df = self.df[['MO','SC','UA','PD','AD']]
            self.sum_df = self.trim_df.apply(lambda c: c.value_counts().reindex(range(1,6), fill_value = 0)).T
    
    def simple_desc(self):
        #Provide a combined table which shows the n and % of people who responded with each datatype, for a single group (e.g. pre-op)
        df = self.sum_df
        as_percent = df.div(df.sum(axis=0),axis=1).mul(100).round(1)
        
        simple_profile = df.astype(str)+ "(" + as_percent.astype(str) + "%)"
        return simple_profile
    
    def binary_desc(self):
        #Create a table which groups problem (1) vs none (2-5), for a single group (e.g. pre-op)
        df = self.sum_df

        binary_profile = pd.DataFrame({'No problems':df.iloc[0,:], 'Problems':df.iloc[1:,:].sum()})
        binary_profile.index = df.index
        binary_profile['% problems'] = (binary_profile['Problems'] / (binary_profile['No problems']+ binary_profile['Problems'])).mul(100).round(1)
            
        return binary_profile
    
    def ts_binary(self):
        #Accepts a complete dataset, calculate the binary % for each group.
        df = self.df
        pct_res = {}
        num_res = {}

        dimensions = ['MO','SC','UA','PD','AD']
        for group, group_data in df.groupby(self.group_col):
            this_group_pct = {}
            this_group_num = {}
            for dimension in dimensions:
                pct = (group_data[dimension]==1).sum() / len(group_data)
                this_group_pct[dimension] = pct

                num = (group_data[dimension]==1).sum()
                this_group_num[dimension] = num

            num_res[group] = this_group_num
            pct_res[group] = this_group_pct
        
        #df1 output = %
        df1 = pd.DataFrame(pct_res).T

        #df2 output = n
        df2 = pd.DataFrame(num_res).T

        return df2
    




