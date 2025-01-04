class eq5dvalue:
#This class will deal with eq5d values.
#THe input will be some data containing eq5d profiles, the country label, and the value set
#the output will be a df, which contains the util values mapped to the original UIDs.

    def __init__(self, data, valueset ,country='NewZealand'):
        self.value_set = valueset
        self.data = data
        self.country = country

    def calculate_util(self):
        #this function will calculate the utility values for each patient, based on the weights and the profile.
        #return a new df which has the util value appended to the original data.
        country = self.country
        val = self.value_set
        val.set_index('INDEX',inplace=True)

        df = self.data
        util_values = []

        for index,row in df.iterrows():
            key= row['INDEXPROFILE']
            util_values.append(val.loc[key,country])
        df['UTILITY'] = util_values
        return df
