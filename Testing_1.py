import matplotlib.pyplot as plt
import seaborn as sns

# Set the style of seaborn
sns.set(style="whitegrid")

# Create the plot
plt.figure(figsize=(10, 10))

# Create a scatter plot with seaborn
scatter = sns.scatterplot(data=df, x='postop_score', y='preop_score', 
                          hue='change', palette={'Improved': 'green', 
                                                  'Worse': 'red', 
                                                  'No Change': 'orange'},
                          style='change', s=100)

# Annotate each point with patient ID
for i in range(len(df)):
    scatter.text(df['postop_score'][i], df['preop_score'][i], 
                 df['patient_id'][i], 
                 horizontalalignment='center', 
                 size='medium', 
                 color='black', 
                 weight='semibold')

# Draw the 45-degree line
plt.plot([1, 3125], [1, 3125], color='black', linestyle='--', linewidth=1)

# Set limits and labels
plt.xlim(1, 3125)
plt.ylim(1, 3125)
plt.xlabel('Postoperative Scores')
plt.ylabel('Preoperative Scores')
plt.title('Health Profile Grid')

# Add legend
plt.legend(title='Change Classification')

# Show the plot
plt.grid()
plt.show()