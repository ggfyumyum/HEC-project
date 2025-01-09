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
       
    def paretian(self,group1,group2):
        #input name of group1 data, name of group2 data
        #outputs a trimmed df showing the paretian classification of group1 vs group2 index profile.

        if len(self.siloed_data)!=2:
            print("TO run paretian analysis requires g  = 2")
            return

        df1 = self.siloed_data[group1]
        df2 = self.siloed_data[group2]

        df = pd.merge(df1,df2,on=['UID'])

        df[group1] = df['INDEXPROFILE_x']
        df[group2] = df['INDEXPROFILE_y']

        df = df[['UID','Preop','Postop']]
        df.set_index(['UID'],inplace=True)

        def check_paretian(row,group1,group2):

            baseline = list(str(row[group1]))
            follow = list(str(row[group2]))

            delta = [int(g2) - int(g1) for g1, g2 in zip(baseline, follow)]

            if all (d==0 for d in delta):
                return "Same"
            
            elif all (d>0 for d in delta):
                return "Worse"
            
            elif all (d<0 for d in delta):
                return "Better"
            
            return "Mixed/uncategorised"

        df['Paretian class'] = df.apply(check_paretian,axis=1,group1=group1,group2=group2)

        return df
    
    def top_frequency (self):
        #input whole dataframe
        #output top 10 frequency indexprofiles
        x = pd.Series(self.df['INDEXPROFILE'])
        top_10_index = x.value_counts().head(10)
        return top_10_index
    
    def hpg(self, paretian_df,group1='Preop',group2='Postop'):
        #This function requires a special input, paretian classification input and util ranking
        #outputs a df which can be used to create a health profile grid

        df = self.df

        df_1 = df[df[self.group_col]==group1]
        df_2 = df[df[self.group_col]==group2]
        
        paretian_df['preop_ranking'] = paretian_df.index.map(df_1.set_index('UID')['RANKED_UTILITY'])
        paretian_df['postop_ranking'] = paretian_df.index.map(df_2.set_index('UID')['RANKED_UTILITY'])

        paretian_df.to_csv('xyz.csv')

        return paretian_df
    
    def level_sum_score(self):
        dimensions = ['MO','SC','UA','PD','AD']
        self.df['level_sum_score'] = self.df[dimensions].sum(axis=1)
        return self.df
        

        return


    #todo 

    #cumulative frequency - DONE
    #paretian classification - DONE
    #health profile grid - DONE
    #level sum score
    #level frequency score

    #EQ VAS
    #simple descriptive statistics


    #extra
    #shannons indices
    #health state density curve
    #EQVAS - regression analysis
    #group by demographic

    #heteroskedacitiy
    #regression analysis





