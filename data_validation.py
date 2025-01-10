import pandas as pd
import datetime as dt

class Validator:
    
    def __init__(self, raw_data, multiple_groups,group_col):

        #inputs = raw data, name of the column which the groups are in
        self.data = raw_data
        self.multiple_groups = multiple_groups
        self.group_col = group_col
        self.validate_data()
        self.group_list = self.check_groups()
        
    def validate_data(self):
        # stop the program if raw data does not have required dimensions

        required_columns = ['MO', 'SC', 'UA', 'PD', 'AD']
        if not all(column in self.data.columns for column in required_columns):
            raise ValueError('Data missing required dimension columns, required format MO, SC, UA, PD, AD')

        if pd.DataFrame(self.data).shape[1]<2:
            raise ValueError('Invalid data input')

    def check_groups(self):
        if not self.multiple_groups:
            print('Single group specified')
            return []
        
        group_col = self.data[self.group_col]
        unique_values = group_col.unique().tolist()

        print('Multiple groups detected',unique_values)
        return unique_values
        
    def clean_data(self):
        pass

    def get_data(self):
        return self.data
    
    def transpose_data(self):
        pass
    #this function can be called if the data is in a longitudinal format






    
