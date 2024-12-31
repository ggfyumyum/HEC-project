import pandas as pd

df = pd.read_excel('VS_decrements.xlsx')

df.fillna(0, inplace=True)

df = df.iloc[2:,:]

print(df)

#generates value set from decrement table
