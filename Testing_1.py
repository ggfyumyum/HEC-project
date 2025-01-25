import pandas as pd

from data_generator import Generator

res = Generator.generate_data(5,2)

res.to_csv('fakedata2.csv')