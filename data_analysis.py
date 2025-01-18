import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#the functions in this class accept raw dataframe, and extract some type of statistics/analysis
#the functions return dataframes which directly show summary statistics, or which can be sent to vizualisation

class Processor:

    def __init__(self, data, group_list=[],group_col='None'):

        #The processor can accept two types of data, one type is the entire dataset. The other is a dataset containing a single group, for example only pre-op patients. 
        self.df = pd.DataFrame(data)
        self.group_col = group_col
        self.group_list = group_list
        if group_col == 'AGE':
            #change age to groups
            pass


        #If there are multiple groups detected, split the data into dataframes with one group each
        if len(group_list)>1:
            self.siloed_data = {group: data for group, data in self.df.groupby(self.group_col)}
        
        else:
        #If the dataset passed is a single group, do some modification to assist for later single-group analysis.
        #Note if original data passed is a dictionary,
            self.trim_df = self.df[['MO','SC','UA','PD','AD']]
            self.sum_df = self.trim_df.apply(lambda c: c.value_counts().reindex(range(1,6), fill_value = 0)).T
    
    def cont_to_cat(self):
        #change age to agegroup
        df = self.df
        return
    
    def simple_desc(self):
        #Provide a combined table which shows the n and % of people who responded with each score, for each dimension, for a single group (e.g. pre-op)
        df = self.sum_df
        as_percent = df.div(df.sum(axis=0),axis=1).mul(100).round(1)
        
        simple_profile = df.astype(str)+ "(" + as_percent.astype(str) + "%)"
        return simple_profile
    
    def get_percent(self):
        return self.sum_df.div(self.sum_df.sum(axis=0),axis=1).mul(100).round(1)
    
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
       
    def paretian(self):
        #outputs a trimmed df showing the paretian classification of group1 vs group2 index profile.
        try:
            if len(self.group_list)!=2:
                raise ValueError('cant create paretian df if group count!=2')
        
            group_1 = self.group_list[0]
            group_2 = self.group_list[1]

            df1 = self.siloed_data[group_1]
            df2 = self.siloed_data[group_2]

            df = pd.merge(df1,df2,on=['UID'])

            df[group_1] = df['INDEXPROFILE_x']
            df[group_2] = df['INDEXPROFILE_y']

            df = df[['UID',group_1,group_2]]
            df.set_index(['UID'],inplace=True)

            def check_paretian(row,group_1,group_2):

                baseline = list(str(row[group_1]))
                follow = list(str(row[group_2]))

                delta = [int(g2) - int(g1) for g1, g2 in zip(baseline, follow)]

                if all (d==0 for d in delta):
                    return "Same"
                
                elif all (d>0 for d in delta):
                    return "Worse"
                
                elif all (d<0 for d in delta):
                    return "Better"
                
                return "Mixed/uncategorised"

            df['Paretian class'] = df.apply(check_paretian,group_1=group_1,group_2=group_2,axis=1)
            return df
        except ValueError as e:
            print(f"Error:{e}")
            return None
    
    def top_frequency (self):
        #input whole dataframe
        #output top 10 frequency indexprofiles
        x = pd.Series(self.df['INDEXPROFILE'])
        top_10_index = x.value_counts().head(10)
        return top_10_index
    
    def hpg(self, paretian_df,group1='Preop',group2='Postop'):
        #This function requires a special input, paretian classification input and util ranking
        #outputs a df which can be used to create a health profile grid
        #adj input parameters

        df = self.df

        df_1 = df[df[self.group_col]==group1]
        df_2 = df[df[self.group_col]==group2]
        
        paretian_df['preop_ranking'] = paretian_df.index.map(df_1.set_index('UID')['TOTAL_RANKED_UTILITY'])
        paretian_df['postop_ranking'] = paretian_df.index.map(df_2.set_index('UID')['TOTAL_RANKED_UTILITY'])

        paretian_df.to_csv('xyz.csv')

        hpg_df = paretian_df

        print(hpg_df)

        return hpg_df
    
    def level_sum_score(self):
        dimensions = ['MO','SC','UA','PD','AD']
        self.df['level_sum_score'] = self.df[dimensions].sum(axis=1)
        return self.df
    
    def level_frequency_score(self):
        dimensions= ['MO','SC','UA','PD','AD']

        def calculate_freq(row):

            count = [0]*5
            for dim in dimensions:
                value = row[dim]
                if 0<value<6:
                    count[value-1]+=1
            freq = ''.join(str(d) for d in count)

            #keep freq as str to preserve leading zeros
            return (freq)
        self.df['level_frequency_score'] = self.df.apply(calculate_freq, axis=1)
        return self.df
    
    def ts_utility(self):
        df = self.df

        avg_utility= df.groupby(self.group_col)['UTILITY'].mean().reset_index()
        avg_utility.columns = [self.group_col,'average_utility_score']

        return avg_utility
    
    def ts_eqvas(self):
        df = self.df
        avg_eqvas = df.groupby(self.group_col)['EQVAS'].mean().reset_index()
        avg_eqvas.columns = [self.group_col,'average_EQVAS_score']

        return avg_eqvas
    
    def health_state_density_curve(self):
        df = self.df
        groups = self.group_list
        cumulative_data = []

        for group in groups:
            if len(groups)>1:
                group_df = df[df[self.group_col]==group]
            else:
                group_df = df

            profile_counts = group_df['INDEXPROFILE'].value_counts().reset_index()
            profile_counts.columns = ['INDEXPROFILE', 'frequency']
            profile_counts = profile_counts.sort_values(by='frequency', ascending=False).reset_index(drop=True)
            
            profile_counts['cumulative_frequency'] = profile_counts['frequency'].cumsum() / profile_counts['frequency'].sum()
            profile_counts['cumulative_obs'] = (profile_counts.index + 1) / len(profile_counts)
            group_df = profile_counts
            group_df['group'] = group
            cumulative_data.append(group_df[['cumulative_frequency', 'cumulative_obs', 'group']])
        
        cumulative_df = pd.concat(cumulative_data)

        return cumulative_df

    def utility_density(self):
        df = self.df
        df['rounded_utility'] = df['UTILITY'].round(2)
        return df


    #todo 

    #cumulative frequency - DONE
    #paretian classification - DONE
    #health profile grid - DONE
    #level sum score - DONE
    #level frequency score - DONE
    #Time series utility - DONE
    #EQ VAS time series - DONE
    #simple descriptive statistics - DONE
    #data validation - DONE

    #error handling - DONE
    #missing imputation - DONE
    #group by demographic - DONE

    #country select validation
    #flexible country selection
    #statsitical analysis of density plot
    #bias data generator

    #extra
    #shannons indices
    #health state density curve - DONE
    #EQVAS - regression analysis


    #heteroskedacitiy
    #regression analysis





