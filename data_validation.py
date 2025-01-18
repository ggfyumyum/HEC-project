import pandas as pd
import datetime as dt

class Validator:
    
    def __init__(self, raw_data,group_col='None'):

        #inputs = raw data, name of the column which the groups are in
        self.data = raw_data
        self.group_col = group_col
        self.required_columns = ['MO', 'SC', 'UA', 'PD', 'AD','EQVAS']
        self.validate_data()
        self.check_groups()
        self.data = self.check_data()
        
    def validate_data(self):
        # stop the program if raw data does not have required dimensions

        if not all(column in self.data.columns for column in self.required_columns):
            raise ValueError('Data missing required dimension columns, required format MO, SC, UA, PD, AD, EQVAS')

        if pd.DataFrame(self.data).shape[1]<2:
            raise ValueError('Invalid data input')

    def check_groups(self):
        if self.group_col == 'None':
            self.group_list = ['Whole_dataset']
            return
        group_col = self.data[self.group_col]
        unique_values = group_col.unique().tolist()
        self.group_list = unique_values
        return


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






    
