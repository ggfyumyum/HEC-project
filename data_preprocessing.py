import pandas as pd
import datetime as dt

class Validator:
    
    def __init__(self, raw_data):
        self.data = raw_data

        self.validate_data()
        self.merge,self.xset,self.yset = self.preprocess_data()

        #check the group label column to see how many groups there are, and send the data into an array
        self.groups = self.data['TIME_INTERVAL'].unique()

    def validate_data(self):
        #this function always runs, and it checks if the input (raw data) meets the critical requirements. If it doesn't, it raises an error and stops the whole program.
        #we need to check if there are index values not matching the profile, and what to do accordingly.
        required_dimensions = True
        if pd.DataFrame(self.data).shape[1]<2:
            required_dimensions = False

        if not required_dimensions:
            raise ValueError('not meeting data requirements')
        

    def preprocess_data(self):
        df = pd.DataFrame(self.data)

        # can we write a way to detect automatically if the data has timestamps or UID
        #the user should specify to us what the groups are and time interval format.
        
        #split into two new datasets based on grouping
        #issue is that the groups won't always be called "Group 1 or Group 2"
        out = []
        for group in self.groups:
            self.group = df[df['TIME_INTERVAL']==group]

        return
    
    def transpose_data(self):
        pass
    #this function can be called if the data is in a longitudinal format






    
