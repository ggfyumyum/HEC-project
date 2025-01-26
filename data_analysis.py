import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

class Processor:

    """
    A class used to process data and extract statistics/analysis.
    Returns dataframes which directly show summary statistics, or which can be sent to vizualisation

    Attributes:
    df (pd.DataFrame): The data to be processed.
    group_column (str): The column used to group the data.
    group_list (list): List of unique groups in the group_column.
    sum_df (pd.DataFrame): Summary DataFrame of the trimmed data.
    siloed_data (dict): Dictionary of dataframes split by group.
    """
    

    def __init__(self, data: pd.DataFrame,group_column: str='None',reverse_grouplist: bool=False):
        """
        Initialize the Processor with data and an optional group column.

        The processor can accept two types of data, one type is the entire dataset. 
        The other is a dataset containing a single group, for example only pre-op patients. 

        Parameters:
        data (pd.DataFrame): The data to be processed.
        group_column (str, optional): The column used to group the data. Defaults to 'None'.
        """
        
        self.df = pd.DataFrame(data)
        self.group_column = group_column

        self.trim_df = self.df[['MO','SC','UA','PD','AD']]
        self.sum_df = self.trim_df.apply(lambda c: c.value_counts().reindex(range(1,6), fill_value = 0)).T

        if self.group_column == 'None':
            self.group_list = ['NO_GROUP_CHOSEN']
        else:
            group_list = self.df[self.group_column].unique().tolist()
            self.group_list = [str(x) for x in group_list]

        self.reversed_grouplist = list(reversed(self.group_list))

        if reverse_grouplist:
            self.group_list = self.reversed_grouplist
        #If there are multiple groups detected, split the data into dataframes with one group each
        if len(self.group_list)>1:
            self.siloed_data = {str(group): data for group, data in self.df.groupby(self.group_column)}
    
    def simple_desc(self):
        """
        Provide a combined table which shows the n and % of people who responded with each score, for each dimension, for a single group (e.g. pre-op).

        Returns:
        pd.DataFrame: DataFrame containing the summary statistics.
        """
        df = self.sum_df
        as_percent = df.div(df.sum(axis=0),axis=1).mul(100).round(1)
        simple_profile = df.astype(str)+ "(" + as_percent.astype(str) + "%)"
        return simple_profile
    
    def get_percent(self):
        """
        Calculate the percentage of responses for each score, for each dimension. The output of this used to create timeseries.

        Returns:
        pd.DataFrame: DataFrame containing the percentage of responses.
        """
        return self.sum_df.div(self.sum_df.sum(axis=0),axis=1).mul(100).round(1)
    
    def binary_desc(self):
        """
        Create a table which groups problem (1) vs no problems (2-5), for a single group (e.g. pre-op).

        Returns:
        pd.DataFrame: DataFrame containing the binary summary statistics.
        """
        #Create a table which groups problem (1) vs none (2-5), for a single group (e.g. pre-op)
        df = self.sum_df

        binary_profile = pd.DataFrame({'No problems':df.iloc[0,:], 'Problems':df.iloc[1:,:].sum()})
        binary_profile.index = df.index
        binary_profile['% problems'] = (binary_profile['Problems'] / (binary_profile['No problems']+ binary_profile['Problems'])).mul(100).round(1)
            
        return binary_profile
    
    def ts_binary(self):
        """
        Calculate the binary percentage change for each group over time.

        Returns:
        Dict[str, pd.DataFrame]: Dictionary containing the binary percentage for each group.
        """
        df = self.df
        pct_res = {}
        num_res = {}

        dimensions = ['MO','SC','UA','PD','AD']
        for group, group_data in df.groupby(self.group_column):
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
        df1 = pd.DataFrame(pct_res).T.reset_index()

        #df2 output = n, not used but accessible.
        df2 = pd.DataFrame(num_res).T.reset_index()

        return df1
       
    def paretian(self):
        """
        Classify patients into Paretian classes based on their health status.

        Returns:
        Optional[pd.DataFrame]: DataFrame containing the Paretian classification, or None if an error occurs.
        """
        try:
            if len(self.group_list)!=2:
                raise ValueError('cant create paretian df if group count!=2')
            
            group_1 = self.group_list[0]
            group_2 = self.group_list[1]
            
            df1 = self.siloed_data[group_1]
            df2 = self.siloed_data[group_2]

            #if the different groups do not have matching UIDs, we cant create the paretian DF.
            print('df1',df1)
            print('df2',df2)
        
            if set(df1['UID']) != set(df2['UID']):
                raise ValueError('invalid grouping selection for comparison')
            

            df = pd.merge(df1,df2,on=['UID'])

            df[f'{group_1}_INDEX'] = df['INDEXPROFILE_x']
            df[f'{group_2}_INDEX']= df['INDEXPROFILE_y']

            df = df[['UID',f'{group_1}_INDEX',f'{group_2}_INDEX']]
            df.set_index(['UID'],inplace=True)

            def check_paretian(row,group_1,group_2):
                #ideally would add the ability for user to discern which group is baseline, and which is followup.

                baseline = list(str(row[f'{group_1}_INDEX']))
                followup = list(str(row[f'{group_2}_INDEX']))

                delta = [int(g2) - int(g1) for g1, g2 in zip(baseline, followup)]
 
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
        """
        Calculate the top 10 frequency index profiles.

        Returns:
        pd.Series: Series containing the top 10 frequency index profiles.
        """
        x = pd.Series(self.df['INDEXPROFILE'])
        top_10_index = x.value_counts().head(10)
        return top_10_index
    
    def hpg(self, paretian_df: pd.DataFrame ,group_1:str = 'Preop',group_2:str ='Postop'):
        """
        Create a Health Profile Grid (HPG) based on Paretian classification and utility ranking.

        Parameters:
        paretian_df (pd.DataFrame): DataFrame containing the Paretian classification.
        group1 (str, optional): The first group for comparison. Defaults to 'Preop'.
        group2 (str, optional): The second group for comparison. Defaults to 'Postop'.

        Returns:
        None
        """
        df = self.df

        df_1 = df[df[self.group_column]==group_1]
        df_2 = df[df[self.group_column]==group_2]

        paretian_df[f'{group_1}_RANK_SCORE'] = paretian_df.index.map(df_1.set_index('UID')['TOTAL_RANKED_UTILITY'])
        paretian_df[f'{group_2}_RANK_SCORE'] = paretian_df.index.map(df_2.set_index('UID')['TOTAL_RANKED_UTILITY'])

        hpg_df = paretian_df[[f'{group_1}_INDEX',f'{group_2}_INDEX',f'{group_1}_RANK_SCORE',f'{group_2}_RANK_SCORE','Paretian class']]
        return hpg_df
    
    def level_sum_score(self):
        """
        Calculate the level sum score for each dimension.

        Returns:
        pd.DataFrame: DataFrame containing the level sum score for each dimension.
        """
        dimensions = ['MO','SC','UA','PD','AD']
        self.df['level_sum_score'] = self.df[dimensions].sum(axis=1)
        return self.df
    
    def level_frequency_score(self):
        """
        Calculate the level frequency score for each dimension.

        Returns:
        pd.DataFrame: DataFrame containing the level frequency score for each dimension.
        """
        dimensions= ['MO','SC','UA','PD','AD']
        def calculate_freq(row):
            count = [0]*5
            for dim in dimensions:
                value = int(row[dim])
                if 0<value<6:
                    count[value-1]+=1
            #keep freq as str to preserve leading zeros
            freq = ''.join(str(d) for d in count)
            return (freq)
        self.df['level_frequency_score'] = self.df.apply(calculate_freq, axis=1)
        return self.df
    
    def ts_utility(self):
        """
        Calculate the average utility score for each group in the group column

        Returns:
        pd.DataFrame: DataFrame containing the utility scores.
        """
        df = self.df
        utility_mean= df.groupby(self.group_column)['UTILITY'].mean()
        utility_counts = df.groupby(self.group_column)['UTILITY'].count()
        utility_sem = df.groupby(self.group_column)['UTILITY'].sem()

        confidence_level = 0.95
        degrees_freedom = utility_counts - 1
        crit_value = stats.t.ppf((1 + confidence_level) /2, degrees_freedom)
        margin_error = utility_sem * crit_value

        avg_utility = pd.DataFrame({
            self.group_column: utility_mean.index,
            'average_UTILITY_score':utility_mean.values,
            'ci_lower': utility_mean.values - margin_error.values,
            'ci_upper': utility_mean.values + margin_error.values
        })

        return avg_utility
    
    def ts_eqvas(self):
        """
        Calculate the time series of EQ-VAS scores.

        Returns:
        pd.DataFrame: DataFrame containing the time series of EQ-VAS scores.
        """
        df = self.df
        eqvas_mean = df.groupby(self.group_column)['EQVAS'].mean()
        eqvas_counts = df.groupby(self.group_column)['EQVAS'].count()
        eqvas_sem = df.groupby(self.group_column)['EQVAS'].sem()

        confidence_level = 0.95
        degrees_freedom = eqvas_counts - 1
        crit_value = stats.t.ppf((1 + confidence_level) /2, degrees_freedom)
        margin_error = eqvas_sem * crit_value

        avg_eqvas = pd.DataFrame({
            self.group_column: eqvas_mean.index,
            'average_EQVAS_score':eqvas_mean.values,
            'ci_lower': eqvas_mean.values - margin_error.values,
            'ci_upper': eqvas_mean.values + margin_error.values
        })

        return avg_eqvas
    
    def health_state_density_curve(self):
        """
        Calculate the health state density curve.

        Returns:
        pd.DataFrame: DataFrame containing the health state density curve.
        """
        df = self.df
        groups = self.group_list
        cumulative_data = []

        for group in groups:
            if len(groups)>1:
                group_df = df[df[self.group_column]==group]
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
        """
        Used to create nicer utility values for the visualisation function to plot the density curves.

        Returns:
        pd.DataFrame: DataFrame containing the utility density.
        """
        df = self.df
        df['rounded_utility'] = df['UTILITY'].round(2)
        return df
    
    def cont_to_cat(self):
        #change age to agegroup, not used.
        df = self.df
        return


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





