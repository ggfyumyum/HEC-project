import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Visualizer:

    def __init__(self,data):
            self.data = data

    def time_series(self):
          df = self.data
          df.set_index(df.columns[0],inplace=True)
          res = sns.lineplot(x=df.index,y=df.columns[0], data=df)
          res.set(xlabel=df.index.name,ylabel=df.columns[0],title=f"Time Series of {df.columns[0]} versus group")
          plt.show()
          return
    
    def hpg(self):
          df = self.data
          plt.figure(figsize=(10,10))
          plot = sns.scatterplot(data = df, x='postop_ranking',y='preop_ranking',hue='Paretian class', palette={'Better': 'green', 'Worse':'red', 'Same':'yellow','Mixed/uncategorised':'blue'},style='Paretian class',s=100)

          plt.plot([1,3125],[1,3125],color='black',linestyle='--',linewidth=1)
          plt.xlim(1,3125)
          plt.ylim(1,3125)
          plt.xlabel('Postop scores')
          plt.ylabel('Postop scores')
          plt.title('Health Profile Grid')
          plt.legend(title='Change in health status')
          plt.grid()
          plt.show()
          return
    
    def histogram(self):
          #produce histogram of each dimension
          
          df = self.data
          df = df.melt(var_name='Level',value_name='Percentage',ignore_index=False).reset_index()
          df.rename(columns={'index':'Dimension'},inplace=True)

          plt.figure(figsize=(12,8))
          sns.barplot(data=df, x='Dimension',y='Percentage',hue='Level',palette='viridis')
          plt.xlabel('Dimension')
          plt.ylabel('Percentage')
          plt.title('Percentage of Each Level by Dimension')
          plt.legend(title='Level')
          plt.grid(axis='y')

          plt.yticks(range(0,51,5))
          plt.show()
          return
    
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

          plt.tight_layout()
          plt.show()
          return

    def health_state_density_curve(self):
          df = self.data
          print(df)
          groups = df[df.columns[2]].unique()
          hsdi_values = {}
          plt.figure(figsize=(10,6))

          for group in groups:
            group_df = df[df[df.columns[2]] == group]
            obs = df.columns[0]
            freq = df.columns[1]
            hsdi = 0
            x_prev, y_prev = 0,0

            for i, row in group_df.iterrows():
                  x_i = row[obs]
                  y_i = row[freq]
                  hsdi+=(x_i-x_prev) * (y_i+ y_prev)
                  x_prev, y_prev = x_i, y_i
            hsdi_values[group] = hsdi
            print('hsdi values',hsdi_values)  
            sns.lineplot(data=group_df,x=obs,y=freq, label=f'{group} (HSDI = {hsdi:.2f})')

          plt.plot([0,1],[0,1], color='black',linestyle='-')
          plt.xlabel('Cumulative Proportion of Observations')
          plt.ylabel('Cumulative Proportion of Profiles')
          plt.title('Health State Density Curve')
          plt.show()

          return
            
            

            