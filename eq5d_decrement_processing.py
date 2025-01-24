import pandas as pd
import itertools

class Decrement_processing:
    """
    A class used to process raw decrement value tables.

    Attributes:
    data (pd.DataFrame): The raw decrement data.
    value_set (Dict[str, Any]): The generated value set.
    """

    def __init__(self,data: pd.DataFrame):
        """
        Initialize the DecrementProcessing with data.

        Parameters:
        data (pd.DataFrame): The raw decrement data.
        """
        self.data = data
        self.value_set = {}
        self.data.fillna(0,inplace=True)
        self.data = self.data.iloc[2:,:]

    def generate_value_set(self):
        """
        Generate a value set from the decrement table.

        Returns:
        pd.DataFrame: The generated value set.
        """
        df = self.data
        df.set_index('LABEL',inplace=True)

        num_list = [f'{A}{B}{C}{D}{E}' for A in range(1, 6) for B in range(1, 6) for C in range(1, 6) for D in range(1, 6) for E in range(1, 6)]
        dimension_list=['MO','SC','UA','PD','AD']

        for country in df.columns:
            country_res = {}
            start_value = df.loc['StartValue', country] if 'StartValue' in df.index else 1
            intercept = df.loc['Intercept', country] if 'Intercept' in df.index else 0

            if pd.notna(intercept):
                start_value+=intercept

            for num in num_list:
                print('starting the loop', 'country=',country)
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




