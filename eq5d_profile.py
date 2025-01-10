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
        self.util_to_rank = self.create_util_ranking()

    def create_util_ranking(self):
        #rank the indexes based on util from 1 to 3125
        #store the result in a hashmap with the key as index, rank as value
        df = pd.DataFrame(self.value_set[self.country])
        df.sort_values(by=self.country,ascending=False,inplace=True)
        df.reset_index(inplace=True)

        result = {row['INDEX']:index +1 for index, row in df.iterrows()}
        return result
    
    def calculate_util(self):
        #this function will calculate the utility values for each patient, based on the weights and the profile.
        #return a new df which has the util value appended to the original data.
        country = self.country
        val = self.value_set
        df = self.data
    
        #append the utility values to the original data
        util_values = []
        for index,row in df.iterrows():
            key= row['INDEXPROFILE']
            util_values.append(val.loc[key,country])
        df['UTILITY'] = util_values
        
        #append the utility rank score to the original data
        ranked_util = []
        for index,row in df.iterrows():
            key= row['INDEXPROFILE']
            ranked_util.append(self.util_to_rank[key])
        df['RANKED_UTILITY'] = ranked_util

        self.utils = df
        return self.utils
    





