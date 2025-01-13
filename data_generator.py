import pandas as pd
import random

print('running data generator')

#fake data generator. This is designed for one group only.

#group count = the number of time intervals measured.
#num is the people per group, NOT the total num.
#make sure uid is same


num = 1000
time_intervals = 2

#generate up to N intervals
intervals = []
for time in range(time_intervals):
    intervals.append('interval'+str(time))

#pre-labelled intervals for N = 3
if time_intervals <=3:
    l = ['Preop','Postop','Future']
    intervals = l[:time_intervals]

gender_assignment = ['M','F']

UID = [i for i in range(1,(num+1))]

d1 = {}
for patient in UID:
    d1[patient] = []

for patient in UID:
    for t in range(time_intervals):
        d1[patient].append([intervals[t],random.randint(1,100),gender_assignment[random.randint(0,1)],random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,5),random.randint(1,100)])

rows = []
for uid, interval in d1.items():
    for interval in interval:
        rows.append([uid] + interval)

column = ["UID",'TIME_INTERVAL','AGE','GENDER',"MO","SC","UA","PD","AD","EQVAS"]

df = pd.DataFrame(rows, columns = column)
df.insert(9,'INDEXPROFILE',df[["MO","SC","UA","PD","AD"]].apply(lambda row: ''.join(row.astype(str)),axis=1))
df.to_csv('fake_data.csv', index=False)

print(df.head(30))
