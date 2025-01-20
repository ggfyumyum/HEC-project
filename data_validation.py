import pandas as pd
import datetime as dt

class Validator:
    
    def __init__(self, raw_data):

        #inputs = raw data, name of the column which the groups are in
        self.data = raw_data
        self.required_columns = ['MO', 'SC', 'UA', 'PD', 'AD','EQVAS']
        self.validate_data()
        self.add_indexprofile()
        self.data = self.check_data()
        
    def validate_data(self):
        # stop the program if raw data does not have required dimensions

        if not all(column in self.data.columns for column in self.required_columns):
            raise ValueError('Data missing required dimension columns, required format MO, SC, UA, PD, AD, EQVAS')

        if pd.DataFrame(self.data).shape[1]<2:
            raise ValueError('Invalid data input')
    
    def add_indexprofile(self):
        if 'INDEXPROFILE' not in self.data.columns:
            self.data['INDEXPROFILE'] = self.data.apply(
                lambda row: f"{row['MO']}{row['SC']}{row['UA']}{row['PD']}{row['AD']}", axis=1
            )

    def check_data(self):
        invalid_values = 0
        missing_values = 0
        for column in self.required_columns[:-1]:
            invalid_values += self.data[column][~self.data[column].between(1,5,inclusive='both')].count()
            missing_values += self.data[column].isna().sum()

        total_errors = invalid_values + missing_values
        EQVAS_error = self.data[self.required_columns[-1]].isna().sum()
        total_errors+=EQVAS_error
        print('total errors identified',total_errors, 'data before',self.data.shape)


        self.data = self.data.dropna(subset=self.required_columns)


        self.data = self.data[self.data[self.required_columns[:-1]].apply(lambda x:x.between(1,5,inclusive='both')).all(axis=1)]

        self.data[self.required_columns] = self.data[self.required_columns].astype(int)
        print('new dataframe',self.data.shape)      
                           
        return self.data
    
    @staticmethod
    def apply_filter(data, group='None', subset='None'):
        if  group!='None' and subset!='None':
            data = data[data[group==subset]]
        return data

    def get_data(self):
        return self.data
    
    def transpose_data(self):
        pass
        #this function can be called if the data is in a longitudinal format






    
