import pandas as pd
import random

#fake data generator

#if there is only one group, then group count = the number of time intervals measured.
#num is the people per group, NOT the total num.
num = 100
time_stamp = 1
group_count = 2

group_list = ['Preop','Postop']
gender_assignment = ['M','F']

UID = [i for i in range(1,(num*group_count)+1)]

d1 = {}
for patient in UID:
    d1[patient] = []

for g in range(group_count):
    for p in range(1,num+1):
        for t in range(time_stamp):
            d1[p + (g*100)].append([group_list[g],t,random.randint(1,100),gender_assignment[random.randint(0,1)],random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,100)])

rows = []
for uid, interval in d1.items():
    for interval in interval:
        rows.append([uid] + interval)

column = ["UID",'GROUP','TIME_INTERVAL','AGE','GENDER',"MO","SC","UA","PD","AD","EQVAS"]

df = pd.DataFrame(rows, columns = column)
df.insert(10,'INDEXPROFILE',df[["MO","SC","UA","PD","AD"]].apply(lambda row: ''.join(row.astype(str)),axis=1))
df.to_csv('fake_data.csv', index=False)

print(df.head(30))