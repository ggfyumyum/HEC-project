import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

class Visualizer:
    """
    A class used to visualize data using various plots.

    Attributes:
    data (pd.DataFrame): The data to be visualized.
    """

    def __init__(self,data):
        """
        Initialize the Visualizer with data.

        Parameters:
        data (pd.DataFrame): The data to be visualized.
        """
        self.data = data.copy()

    def time_series(self):
        """
        Create a time series plot of the data.

        Returns:
        matplotlib.figure.Figure: The figure object containing the time series plot.
        """
        fig, ax = plt.subplots()
        df = self.data
        df.set_index(df.columns[0], inplace=True)

        has_ci = 'ci_lower' in df.columns and 'ci_upper' in df.columns

        if df.shape[1] == 1:
            sns.lineplot(x=df.index, y=df.columns[0], data=df, ax=ax)
            ax.set(xlabel=df.index.name, ylabel=df.columns[0], title=f"Time Series of {df.columns[0]} versus group")

        else:
            for col in df.columns:
                if col not in ['ci_lower', 'ci_upper']:
                    sns.lineplot(x=df.index, y=col, data=df, ax=ax, label=col)
                    if has_ci:
                        ax.fill_between(df.index, df['ci_lower'], df['ci_upper'], alpha=0.3)

            ax.set(xlabel=df.index.name, ylabel='Values', title="Time Series of Multiple Columns")
            ax.legend(title='Columns')
    
    def hpg(self):
        """
        Create a Health Profile Grid (HPG) scatter plot.

        Returns:
        matplotlib.figure.Figure: The figure object containing the HPG scatter plot.
        """
        df = self.data
        fig, ax = plt.subplots(figsize=(10, 10))
        #ranking scores are in column index 2 and 3 respectively
        sns.scatterplot(data=df, x=df.columns[2], y=df.columns[3], hue='Paretian class', 
                        palette={'Better': 'green', 'Worse': 'red', 'Same': 'yellow', 'Mixed/uncategorised': 'blue'}, 
                        style='Paretian class', s=100, ax=ax)
        ax.plot([1, 3125], [1, 3125], color='black', linestyle='--', linewidth=1)
        ax.set_xlim(1, 3125)
        ax.set_ylim(1, 3125)
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(df.columns[1])
        ax.set_title('Health Profile Grid')
        ax.legend(title='Change in health status')
        ax.grid()
        return fig
    

    def histogram(self):
        df = self.data
        df = df.melt(var_name='Level', value_name='Percentage', ignore_index=False).reset_index()
        df.rename(columns={'index': 'Dimension'}, inplace=True)
        fig, ax = plt.subplots()
        sns.barplot(data = df, x='Dimension',y='Percentage', hue='Level', palette='viridis', ax=ax)
        ax.set_title('Histogram of Each Dimension')
        return fig
    
    def histogram_by_group(self):
          group_data_dict = self.data
          #create subplots
          num_groups = len(group_data_dict)
          fig, axes = plt.subplots(1, num_groups,figsize=(12*num_groups,8), sharey=True)

          for ax, (group_name, group_df) in zip(axes, group_data_dict.items()):
                df = group_df.melt(var_name='Level', value_name='Percentage',ignore_index=False).reset_index()
                df.rename(columns={'index':'Dimension'}, inplace = True)

                sns.barplot(data = df, x='Dimension',y='Percentage', hue='Level', palette='viridis', ax=ax)
                ax.set_xlabel('Dimension')
                ax.set_ylabel('Percentage')
                ax.set_title(f'Percentage of Each Level by Dimension - {group_name}')
                ax.legend(title='Level')
                ax.grid(axis='y')

          return fig

    def health_state_density_curve(self):
        df = self.data
        fig, ax = plt.subplots()
        hsdi_values = {}
        obs = df.columns[0]
        freq = df.columns[1]

        for group, group_df in df.groupby(df.columns[2]):
            hsdi = 0
            x_prev, y_prev = 0, 0

            for i, row in group_df.iterrows():
                x_i = row[obs]
                y_i = row[freq]
                hsdi += (x_i - x_prev) * (y_i + y_prev)
                x_prev, y_prev = x_i, y_i
            hsdi_values[group] = hsdi
            sns.lineplot(data=group_df, x=obs, y=freq, label=f'{group} (HSDI = {hsdi:.2f})', ax=ax)

        ax.plot([0, 1], [0, 1], color='black', linestyle='-')
        ax.set_xlabel('Cumulative Proportion of Observations')
        ax.set_ylabel('Cumulative Proportion of Profiles')
        ax.set_title('Health State Density Curve')
        ax.legend()
        return fig
    
    
    def utility_density(self):
        df = self.data
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.kdeplot(data=df, x='rounded_utility', hue=df.columns[2], fill=True, common_norm=False, alpha=0.5, ax=ax)
        ax.set_title("Distribution of Health Utilities by Group", fontsize=16)
        ax.set_xlabel("Health Utility (Rounded to Nearest 0.05)", fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.legend(title="Group", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        return fig
    
            