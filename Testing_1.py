import pandas as pd

from data_generator import Generator

res = Generator.generate_data(100,1)

res.to_csv('postop_better.csv')