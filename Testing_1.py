import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Viz:
    def __init__(self, data):
        self.data = data

    def hpg(self):
        df = self.data
        plt.figure(figsize=(10, 10))
        plot = sns.scatterplot(data=df, x='postop_ranking', y='preop_ranking', hue='Paretian class',
                               palette={'Better': 'green', 'Worse': 'red', 'Same': 'yellow', 'Mixed/uncategorised': 'blue'},
                               style='Paretian class', s=100)

        plt.plot([1, 3125], [1, 3125], color='black', linestyle='--', linewidth=1)
        plt.xlim(1, 3125)
        plt.ylim(1, 3125)
        plt.xlabel('Postop scores')
        plt.ylabel('Preop scores')
        plt.title('Health Profile Grid')
        plt.legend(title='Change in health status')
        plt.grid()
        plt.show()

    def histogram(self):
        df = self.data

        # Melt the DataFrame to convert it from wide format to long format
        df_melted = df.melt(var_name='Level', value_name='Percentage', ignore_index=False).reset_index()
        df_melted.rename(columns={'index': 'Dimension'}, inplace=True)

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

    def histogram_by_group(self):
        group_data_dict = self.data
        # Create subplots
        num_groups = len(group_data_dict)
        fig, axes = plt.subplots(1, num_groups, figsize=(12 * num_groups, 8), sharey=True)

        print('Original data:', group_data_dict)

        for ax, (group_name, group_df) in zip(axes, group_data_dict.items()):
            df = group_df.melt(var_name='Level', value_name='Percentage', ignore_index=False).reset_index()
            df.rename(columns={'index': 'Dimension'}, inplace=True)

            print('DataFrame being plotted:', df)

            sns.barplot(data=df, x='Dimension', y='Percentage', hue='Level', palette='viridis', ax=ax)
            ax.set_xlabel('Dimension')
            ax.set_ylabel('Percentage')
            ax.set_title(f'Percentage of Each Level by Dimension - {group_name}')
            ax.legend(title='Level')
            ax.grid(axis='y')

        plt.tight_layout()
        plt.show()

# Example usage:
# Assuming group_data_dict is a dictionary with group names as keys and DataFrames as values
group_data_dict = {
    'Group 1': pd.DataFrame({
        'Level 1': [21.4, 19.4, 18.4, 17.4, 16.4],
        'Level 2': [19.4, 18.4, 17.4, 16.4, 15.4],
        'Level 3': [18.4, 17.4, 16.4, 15.4, 14.4],
        'Level 4': [17.4, 16.4, 15.4, 14.4, 13.4],
        'Level 5': [16.4, 15.4, 14.4, 13.4, 12.4]
    }, index=['MO', 'SC', 'UA', 'PD', 'AD']),
    'Group 2': pd.DataFrame({
        'Level 1': [22.4, 20.4, 19.4, 18.4, 17.4],
        'Level 2': [20.4, 19.4, 18.4, 17.4, 16.4],
        'Level 3': [19.4, 18.4, 17.4, 16.4, 15.4],
        'Level 4': [18.4, 17.4, 16.4, 15.4, 14.4],
        'Level 5': [17.4, 16.4, 15.4, 14.4, 13.4]
    }, index=['MO', 'SC', 'UA', 'PD', 'AD'])
}

viz = Viz(group_data_dict)
viz.histogram_by_group()