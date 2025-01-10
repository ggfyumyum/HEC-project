import pandas as pd
import datetime as dt

class Validator:
    
    def __init__(self, raw_data):

        #inputs = raw data, name of the column which the groups are in
        self.data = raw_data
        self.validate_data()

    def validate_data(self):
        #this function always runs, and it checks if the input (raw data) meets the critical requirements. If it doesn't, it raises an error and stops the whole program.
        required_dimensions = True
        if pd.DataFrame(self.data).shape[1]<2:
            required_dimensions = False

        if not required_dimensions:
            raise ValueError('not meeting data requirements')
        
    def clean_data(self):
        pass

    def get_data(self):
        return self.data
    
    def transpose_data(self):
        pass
    #this function can be called if the data is in a longitudinal format






    
