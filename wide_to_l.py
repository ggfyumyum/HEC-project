#convert wide to long

import pandas as pd


# Create DataFrame

data = pd.read_csv('knee_rep_filltered.csv')
df = pd.DataFrame(data)
print(df)
# Reshape from wide to long format
df_long = pd.wide_to_long(
    df,
    stubnames=["MO", "SC", "UA", "PD", "AD",'INDEXPROFILE','UTILITYC','EQVAS'],
    i=["UID", "AGE", "GENDER"],
    j="TIME_INTERVAL",
    sep=""
).reset_index()

df_long.to_csv('knee_data.csv')