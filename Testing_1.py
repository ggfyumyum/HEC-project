import pandas as pd

# Sample data for patients
data = {
    'patient_id': [1, 2, 3, 4, 5],
    'preop_score': [100, 200, 300, 400, 500],
    'postop_score': [500, 100, 300, 400, 600]
}

# Create DataFrame
df = pd.DataFrame(data)

# Classify changes
def classify_change(row):
    if row['postop_score'] > row['preop_score']:
        return 'Improved'
    elif row['postop_score'] < row['preop_score']:
        return 'Worse'
    else:
        return 'No Change'

df['change'] = df.apply(classify_change, axis=1)

import matplotlib.pyplot as plt


# Set up the plot
plt.figure(figsize=(10, 10))

# Scatter plot
plt.scatter(df['postop_score'], df['preop_score'], c='blue')

# Add labels for each point
for i in range(len(df)):
    plt.annotate(df['patient_id'][i], (df['postop_score'][i], df['preop_score'][i]))

# Draw the 45-degree line
plt.plot([1, 3125], [1, 3125], color='red', linestyle='--')

# Set limits and labels
plt.xlim(1, 3125)
plt.ylim(1, 3125)
plt.xlabel('Postoperative Scores')
plt.ylabel('Preoperative Scores')
plt.title('Health Profile Grid')
# Map classification to colors
color_map = {
    'Improved': 'green',
    'Worse': 'red',
    'No Change': 'orange'
}

# Set up the plot again
plt.figure(figsize=(10, 10))

# Scatter plot with colors based on classification
for change in df['change'].unique():
    subset = df[df['change'] == change]
    plt.scatter(subset['postop_score'], subset['preop_score'], 
                color=color_map[change], label=change)

# Add labels for each point
for i in range(len(df)):
    plt.annotate(df['patient_id'][i], (df['postop_score'][i], df['preop_score'][i]))

# Draw the 45-degree line
plt.plot([1, 3125], [1, 3125], color='red', linestyle='--')

# Set limits and labels
plt.xlim(1, 3125)
plt.ylim(1, 3125)
plt.xlabel('Postoperative Scores')
plt.ylabel('Preoperative Scores')
plt.title('Health Profile Grid')

# Add legend
plt.legend()

# Add grid
plt.grid()

# Show the plot
plt.show()


# Add grid
plt.grid()

# Show the plot
plt.show()

