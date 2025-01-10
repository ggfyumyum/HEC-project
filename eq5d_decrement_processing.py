import pandas as pd
import itertools

class Decrement_processing:
    #This class houses several functions dealing with raw decrement value tables

    def __init__(self,data):
        self.data = data
        self.value_set = {}
        self.data.fillna(0,inplace=True)
        self.data = self.data.iloc[2:,:]

    def generate_value_set(self):
        #generates value set from decrement table
        #return the value set as df
        df = self.data
        df.set_index('LABEL',inplace=True)

        num_list = [f'{A}{B}{C}{D}{E}' for A in range(1, 6) for B in range(1, 6) for C in range(1, 6) for D in range(1, 6) for E in range(1, 6)]
        dimension_list=['MO','SC','UA','PD','AD']
        #disregard start value, intercept
        
        for country in df.columns:
            country_res = {}
            for num in num_list:
                print('starting the loop', 'country=',country)
                start_value = 1
                ctr = 0
                while ctr<5:
                    start_value += df.loc[f'{dimension_list[ctr]}{num[ctr]}',country]
                    ctr+=1
                country_res[num] = start_value
            self.value_set[country] = country_res

        self.value_set= pd.DataFrame(self.value_set)

        self.value_set.index = num_list
        self.value_set.index.name = "INDEX"

        return self.value_set
    

    @staticmethod
    def export_value_set(value_set):
        value_set.to_csv('valueset_data.csv', index=True)
        return




