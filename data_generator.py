import pandas as p_d
import random

# Parameters
num = 100  # Number of patients
time_intervals = 4  # Number of time intervals

# Time intervals
l = ['Preop', 'Postop', 'Future']
if time_intervals<4:
    intervals = l[:time_intervals]
else:
    intervals = [f'interval{i}' for i in range(time_intervals)]

# Gender assignment
gender_assignment = ['M', 'F']

# Unique IDs
UID = [i for i in range(1, (num + 1))]

# Dictionary to store patient data
d1 = {}
for patient in UID:
    d1[patient] = []

# Generate random gender, age, and EQVAS for each UID
patient_info = {}
for patient in UID:
    gender = gender_assignment[random.randint(0, 1)]
    age = random.randint(1, 100)
    eqvas = random.randint(1, 100)
    patient_info[patient] = [gender, age, eqvas]

# Generate random MO, SC, UA, PD, AD for each time interval
for patient in UID:
    gender, age, eqvas = patient_info[patient]
    for t in range(time_intervals):
        mo = random.randint(1, 5)
        sc = random.randint(1, 5)
        ua = random.randint(1, 5)
        pd = random.randint(1, 5)
        ad = random.randint(1, 5)
        d1[patient].append([intervals[t], age, gender, mo, sc, ua, pd, ad, eqvas])

# Create rows for DataFrame
rows = []
for uid, interval in d1.items():
    for interval in interval:
        rows.append([uid] + interval)

# Define column names
columns = ["UID", "TIME_INTERVAL", "AGE", "GENDER", "MO", "SC", "UA", "PD", "AD", "EQVAS"]

# Create DataFrame
df = p_d.DataFrame(rows, columns=columns)
df.insert(9, 'INDEXPROFILE', df[["MO", "SC", "UA", "PD", "AD"]].apply(lambda row: ''.join(row.astype(str)), axis=1))
df.to_csv('fake_data.csv', index=False)

print(df.head(30))
