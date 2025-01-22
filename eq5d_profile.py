import pandas as pd
class Eq5dvalue:
    """
    This class calculates utility values for EQ-5D profiles based on a given value set and country.

    Attributes:
    value_set (pd.DataFrame): The value set containing utility weights.
    data (pd.DataFrame): The input data containing EQ-5D profiles.
    country (str): The country label for which the utility values are calculated.
    """
    def __init__(self, data: pd.DataFrame, valueset:pd.DataFrame ,country='NewZealand'):
        """
        Initializes the Eq5dvalue class with the given data, value set, and country.
        
        Args:
            data (pd.DataFrame): The input data containing EQ-5D profiles.
            valueset (pd.DataFrame): The value set containing utility weights.
            country (str): The country label for which the utility values are calculated. Default is 'NewZealand'.

        """
        self.value_set = valueset
        if 'INDEX' in self.value_set.columns:
            self.value_set.set_index('INDEX',inplace=True)
    
        self.data = data
        self.country = country
  

    def calculate_util(self):
        """
        Calculates the utility values for each patient based on the weights and the profile.
        
        Returns:
            pd.DataFrame: A new DataFrame with the utility values appended to the original data.
        Raises:
            KeyError: If 'INDEXPROFILE' is not found in the data columns.
            KeyError: If the 'country' is not found in the value set columns.
        """

  
        df = self.data

        if 'index' in df.columns:
            df = df.drop(columns=['index'])



        if 'INDEXPROFILE' not in df.columns:
            raise KeyError("The data must contain an 'INDEXPROFILE' column.")
        if self.country not in self.value_set.columns:
            raise KeyError(f"The value set must contain a column for the country '{self.country}'.")
    
        #append the utility values to the original data
        self.util_values = []
        for index,row in df.iterrows():
            key= int(row['INDEXPROFILE'])
            self.util_values.append(self.value_set.loc[key,self.country])
        df['UTILITY'] = self.util_values

        def create_util_ranking(utility_list):
            """
            Ranks the utility scores from 1 to n for a given list of utility scores.
            
            Args:
                utility_list (list): A list of utility scores.
            
            Returns:
                dict: A dictionary with the index profile as the key and the rank as the value.
            """
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

        #also creates rank out of the TOTAL list of utilities for given country (used for HPG creation)
        total_ranking_df = self.value_set[self.country].reset_index().rename(columns={self.country: 'UTILITY'})
        total_ranking_df.sort_values(by='UTILITY', ascending=False, inplace=True)
        total_ranking_df.reset_index(drop=True, inplace=True)

        total_util_ranking = {row['INDEX']: index + 1 for index, row in total_ranking_df.iterrows()}

        total_ranked_util = []
        for index, row in df.iterrows():
            key = int(row['INDEXPROFILE'])
            total_ranked_util.append(total_util_ranking[key])
        df['TOTAL_RANKED_UTILITY'] = total_ranked_util

        self.data = df
        return df



