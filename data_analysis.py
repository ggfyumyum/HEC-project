import pandas as pd

#report the number and percentage of patients reporting each level of problem on each dimension
class Processor:

    def __init__(self, data, group_col='Default'):
        #the input is a dataframe
        self.df = pd.DataFrame(data)
        self.group_col = group_col

        #for each group identified in the group column, create a new dataframe with only that group and add all the dataframes to a dictionary.
        #Only need do this if the data has multiple groups
        if group_col!='Default':
            self.siloed_data = {group: data for group, data in self.df.groupby(self.group_col)}
        
        else:
        #if the dataset passed is a single group, do some modification to assist for later single-group analysis.
        #value counts = sum the total scores
        #reindex and fill value = replace NaN with 0, Transpose the column headers to rows
            self.trim_df = self.df[['MO','SC','UA','PD','AD']]
            self.sum_df = self.trim_df.apply(lambda c: c.value_counts().reindex(range(1,6), fill_value = 0)).T
    

    def simple_desc(self):
        #provide simple descriptive analysis, for a given time interval.

        df = self.sum_df
        as_percent = df.div(df.sum(axis=0),axis=1).mul(100).round(1)
        #output: a combined table which shows the n and % of people who responded with each datatype.
        simple_profile = df.astype(str)+ "(" + as_percent.astype(str) + "%)"
        return simple_profile
    
    def binary_desc(self):
        #Create a new dataframe which just displays No problems vs 0 problems
        df = self.sum_df

        binary_profile = pd.DataFrame({'No problems':df.iloc[0,:], 'Problems':df.iloc[1:,:].sum()})
        binary_profile.index = df.index
        binary_profile['% problems'] = (binary_profile['Problems'] / (binary_profile['No problems']+ binary_profile['Problems'])).mul(100).round(1)
            
        return binary_profile
    


