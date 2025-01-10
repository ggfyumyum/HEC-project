import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Processor:
    def __init__(self, df):
        self.df = df

    def hsdc(self):
        df = self.df

        # Create the INDEXPROFILE column by concatenating values from other columns
        df['INDEXPROFILE'] = df.apply(lambda row: ''.join(row.values.astype(str)), axis=1)

        # Count the frequency of each health profile
        profile_counts = df['INDEXPROFILE'].value_counts().reset_index()
        profile_counts.columns = ['INDEXPROFILE', 'frequency']

        # Sort the profiles by frequency in descending order
        profile_counts = profile_counts.sort_values(by='frequency', ascending=False).reset_index(drop=True)

        # Calculate the cumulative frequency
        profile_counts['cumulative_frequency'] = profile_counts['frequency'].cumsum() / profile_counts['frequency'].sum()

        # Calculate the cumulative proportion of distinct health profiles
        profile_counts['cumulative_distinct_profiles'] = (profile_counts.index + 1) / len(profile_counts)

        return profile_counts

class Visualizer:
    def __init__(self, data):
        self.data = data

    def health_state_density_curve(self):
        df = self.data
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='cumulative_frequency', y='cumulative_distinct_profiles')
        plt.plot([0, 1], [0, 1], color='black', linestyle='--')  # Add a black diagonal line
        plt.xlabel('Cumulative Proportion of Distinct Profiles')
        plt.ylabel('Cumulative Frequency of Health Profiles')
        plt.title('Health State Density Curve')
        plt.show()

# Example data
data = pd.read_excel('eq5d5l_example.xlsx')
df = pd.DataFrame(data)

# Create an instance of the Processor class
processor = Processor(df)

# Calculate the cumulative frequency and cumulative proportion of distinct health profiles
hsdc_df = processor.hsdc()
print(hsdc_df)

# Create an instance of the Visualizer class
visualizer = Visualizer(hsdc_df)

# Plot the Health State Density Curve
visualizer.health_state_density_curve()