import pandas as pd
import itertools

df = pd.read_excel('VS_decrements.xlsx')

#generates value set from decrement table

df.fillna(0, inplace=True)

#disregard start value, intercept
num_list = [f'{A}{B}{C}{D}{E}' for A in range(1, 6) for B in range(1, 6) for C in range(1, 6) for D in range(1, 6) for E in range(1, 6)]

df = df.iloc[2:,:]
df.set_index('LABEL',inplace=True)

dimension_list=['MO','SC','UA','PD','AD']


res = {}

for country in df.columns:
    country_res = {}

    for num in num_list:
        print('starting the loop', 'country=',country)
        
        start_value = 1

        ctr = 0
        while ctr<5:
            start_value += df.loc[f'{dimension_list[ctr]}{num[ctr]}',country]
            ctr+=1
        country_res[num] = start_value
    res[country] = country_res
res = pd.DataFrame(res)

res.to_csv('valueset_data.csv', index=False)
    #res[country] = k
