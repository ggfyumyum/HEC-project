class eq5dvalue:
#THe input will be some data containing eq5d profiles, the country label, and a set of weights.
#the output will be a df, which contains the util values mapped to the original UIDs.

    def __init__(self, data, dec='Default',country='NZ'):
        self.dec = dec
        self.data = data
        self.country = country
        self.dec = self.validate_weights()

    def validate_weights(self):
        #this function will check if the weights are valid, and if they are not, it will raise an error.
        df = self.dec
        df = df.fillna(0)
        df.set_index('LABEL',inplace=True)
        return df

        
    def calculate_util(self):
        #this function will calculate the utility values for each patient, based on the weights and the profile.
        #return a new df which has the util value appended to the original data.
        #need to add memoization
        country = self.country
        dec = self.dec
        df = self.data

        util_values = []
  
        for index, row in df.iterrows():
            util = 1
            profile_list = [digit for digit in str(df.loc[index,'INDEXPROFILE'])]

            profile = {'MO':profile_list[0],'SC':profile_list[1],'UA':profile_list[2],'PD':profile_list[3],'AD':profile_list[4]}
            for dimension, level in profile.items():
                dec_key = f"{dimension}{level}"
                dec_value = dec.loc[dec_key,country]
                util+=dec_value
            util_values.append(util)
        df['UTILITY'] = util_values

        return df
