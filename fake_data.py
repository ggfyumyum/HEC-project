import pandas as pd
import random

#fake data generator
#num is the people per group, NOT the total num.
num = 100
time_interval = 3
group_count = 2

UID = [i for i in range(1,(num*group_count)+1)]

d1 = {}
for patient in UID:
    d1[patient] = []

for g in range(group_count):
    for p in range(1,num+1):
        for t in range(time_interval):
            d1[p + (g*100)].append([g+1,t,random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,100)])

rows = []
for uid, interval in d1.items():
    for interval in interval:
        rows.append([uid] + interval)

column = ["UID",'GROUP','TIME_INTERVAL',"MO","SC","UA","PD","AD","VAS"]

df = pd.DataFrame(rows, columns = column)

df.to_csv('fake_data.csv', index=False)

print(df.head(30))