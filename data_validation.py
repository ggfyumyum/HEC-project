import pandas as pd
import datetime as dt

class Validator:
    """
    This class validates and processes raw EQ-5D data.

    Attributes:
        data (pd.DataFrame): The input raw data containing EQ-5D profiles.
        required_columns (list): The list of required columns for validation.
    """
    
    def __init__(self, raw_data: pd.DataFrame):
        """
        Initializes the Validator class with the given raw data.
        
        Args:
            raw_data (pd.DataFrame): The input raw data containing EQ-5D profiles.
        
        Raises:
            ValueError: If the raw data does not contain the required columns or has less than 2 columns.
        """

        self.data = raw_data
        self.required_columns = ['MO', 'SC', 'UA', 'PD', 'AD','EQVAS']
        self.validate_data()
        self.add_indexprofile()
        self.data = self.check_missing()
        
    def validate_data(self):
        """
        Validates the raw data to ensure it contains the required columns and has at least 2 columns.
        
        Raises:
            ValueError: If the raw data does not contain the required columns or has less than 2 columns.
        """

        if not all(column in self.data.columns for column in self.required_columns):
            raise ValueError('Data missing required dimension columns, required format MO, SC, UA, PD, AD, EQVAS')

        if pd.DataFrame(self.data).shape[1]<2:
            raise ValueError('Invalid data input')
    
    def add_indexprofile(self):
        """
        Adds an 'INDEXPROFILE' column to the data by concatenating the values of 'MO', 'SC', 'UA', 'PD', and 'AD' columns.
        """
        if 'INDEXPROFILE' not in self.data.columns:
            self.data['INDEXPROFILE'] = self.data.apply(
                lambda row: f"{row['MO']}{row['SC']}{row['UA']}{row['PD']}{row['AD']}", axis=1
            )

    def check_missing(self):
        """
        Checks the data for invalid and missing values in the required columns.
        
        Returns:
            pd.DataFrame: The processed data with invalid and missing values counted.
        

        """
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

    def get_data(self):
        return self.data






    
