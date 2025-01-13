import pandas as pd
class Eq5dvalue:
#This class will have some methods which deal with calculating utility
#THe input will be some data containing eq5d profiles, the country label, and the value set
#the output will be a df, which contains the util values mapped to the original UIDs.

    def __init__(self, data, valueset ,country='NewZealand'):
        self.value_set = valueset
        if 'INDEX' in self.value_set.columns:
            self.value_set.set_index('INDEX',inplace=True)

        self.data = data
        self.country = country
        self.utils = None


    def calculate_util(self):
        #this function will calculate the utility values for each patient, based on the weights and the profile.
        #return a new df which has the util value appended to the original data.
        country = self.country
        val = self.value_set
        df = self.data
    
        #append the utility values to the original data
        self.util_values = []
        for index,row in df.iterrows():
            key= row['INDEXPROFILE']
            self.util_values.append(val.loc[key,country])
        df['UTILITY'] = self.util_values

        def create_util_ranking(utility_list):
            #rank the utility scores from 1 to n for a given list of utility scores
            #store the result in a hashmap with the key as index, rank as value
            df.sort_values(by='UTILITY',ascending=False,inplace=True)
            df.reset_index(inplace=True)
            result = {row['INDEXPROFILE']:index+1 for index, row in df.iterrows()}
            return result
        
        util_to_rank = create_util_ranking(df)
        #append the utility rank score to the original data
        ranked_util = []
        for index,row in df.iterrows():
            key= row['INDEXPROFILE']
            ranked_util.append(util_to_rank[key])
        df['RANKED_UTILITY'] = ranked_util

        #also create a new rank which is the index rank out of the TOTAL list of utilities for given country
        total_ranking_df = val[country].reset_index().rename(columns={country: 'UTILITY'})
        total_ranking_df.sort_values(by='UTILITY', ascending=False, inplace=True)
        total_ranking_df.reset_index(drop=True, inplace=True)

        print(total_ranking_df)

        total_util_ranking = {row['INDEX']: index + 1 for index, row in total_ranking_df.iterrows()}

        total_ranked_util = []
        for index, row in df.iterrows():
            key = row['INDEXPROFILE']
            total_ranked_util.append(total_util_ranking[key])
        df['TOTAL_RANKED_UTILITY'] = total_ranked_util


        self.utils = df
        return self.utils



