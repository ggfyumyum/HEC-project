import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Processor:
    def __init__(self, df, group_col):
        self.df = df
        self.group_col = group_col

    def paretian(self, group1, group2):
        df = self.df.copy()
        df[group1] = df['INDEXPROFILE_x']
        df[group2] = df['INDEXPROFILE_y']
        df = df[['UID', group1, group2]]
        df.set_index(['UID'], inplace=True)

        def check_paretian(row, group1, group2):
            baseline = list(str(row[group1]))
            follow = list(str(row[group2]))
            delta = [int(g2) - int(g1) for g1, g2 in zip(baseline, follow)]

            if all(d == 0 for d in delta):
                return "Same"
            elif all(d > 0 for d in delta):
                return "Worse"
            elif all(d < 0 for d in delta):
                return "Better"
            return "Mixed/uncategorised"

        df['Paretian class'] = df.apply(check_paretian, axis=1, group1=group1, group2=group2)
        return df

    def level_frequency_score(self):
        dimensions = ['MO', 'SC', 'UA', 'PD', 'AD']

        def calculate_freq(row):
            counts = [0] * 5  # Initialize a list to store counts for numbers 1 to 5
            for dim in dimensions:
                value = row[dim]
                if 1 <= value <= 5:
                    counts[value - 1] += 1  # Increment the count for the corresponding value
            freq = ''.join(str(count) for count in counts)
            return int(freq)

        self.df['level_frequency_score'] = self.df.apply(calculate_freq, axis=1)
        return self.df

class Viz:
    def __init__(self, data):
        self.data = data

    def histogram(self):
        df = self.data

        # Example of what the DataFrame looks like before melt
        print("Before melt:")
        print(df)

        # Melt the DataFrame to convert it from wide format to long format
        df_melted = df.melt(var_name='Level', value_name='Percentage', ignore_index=False).reset_index()
        df_melted.rename(columns={'index': 'Dimension'}, inplace=True)

        # Example of what the DataFrame looks like after melt
        print("After melt:")
        print(df_melted)

        # Plot the histogram using seaborn
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df_melted, x='Dimension', y='Percentage', hue='Level', palette='viridis')

        plt.xlabel('Dimension')
        plt.ylabel('Percentage')
        plt.title('Percentage of Each Level by Dimension')
        plt.legend(title='Level')
        plt.grid(axis='y')

        # Customize y-axis ticks to display wider intervals
        plt.yticks(range(0, 101, 5))  # Adjust the range and interval as needed

        plt.show()

# Example usage:
# Assuming percentages_df is correctly formatted with percentages for each level and dimension
percentages_df = pd.DataFrame({
    'Level 1': [21.4, 19.4, 18.4, 17.4, 16.4],
    'Level 2': [19.4, 18.4, 17.4, 16.4, 15.4],
    'Level 3': [18.4, 17.4, 16.4, 15.4, 14.4],
    'Level 4': [17.4, 16.4, 15.4, 14.4, 13.4],
    'Level 5': [16.4, 15.4, 14.4, 13.4, 12.4]
}, index=['MO', 'SC', 'UA', 'PD', 'AD'])

print(percentages_df)
viz = Viz(percentages_df)
viz.histogram()