import random
import pandas as pn

class Generator:
    """
    Generate synthetic patient data.

    Parameters:
    num (int): Number of patients.
    time_intervals (int): Number of time intervals.

    Returns:
    pd.DataFrame: DataFrame containing the generated patient data.
    """
    def _init_(self):
        pass

    @staticmethod
    def generate_data(num=100,time_intervals=5):

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
        d1 = {uid: [] for uid in UID}

        # Generate random gender and age for each UID
        patient_info = {}
        for patient in UID:
            gender = gender_assignment[random.randint(0, 1)]
            age = random.randint(1, 100)
            patient_info[patient] = [gender, age]

        # Generate random MO, SC, UA, PD, AD, and EQVAS for each time interval
        for patient in UID:
            gender, age = patient_info[patient]
            for t in range(time_intervals):
                mo = random.randint(1, 5)
                sc = random.randint(1, 5)
                ua = random.randint(1, 5)
                pd = random.randint(1, 5)
                ad = random.randint(1, 5)
                eqvas = random.randint(0, 100)  # Generate a new EQVAS for each time interval
                d1[patient].append([intervals[t], age, gender, mo, sc, ua, pd, ad, eqvas])

        # Create rows for DataFrame
        rows = []
        for uid, interval in d1.items():
            for interval in interval:
                rows.append([uid] + interval)

        # Define column names
        columns = ["UID", "TIME_INTERVAL", "AGE", "GENDER", "MO", "SC", "UA", "PD", "AD", "EQVAS"]

        # Create DataFrame
        df = pn.DataFrame(rows, columns=columns)
        df.insert(9, 'INDEXPROFILE', df[["MO", "SC", "UA", "PD", "AD"]].apply(lambda row: ''.join(row.astype(str)), axis=1))
        df.to_csv('fake_data.csv', index=False)

        print(df.head(3))
        return df
