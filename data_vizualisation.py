import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Viz:
    #can create general purpose methods (static) and normal methods)
    def __init__(self,data):
            self.data = data
        
    
    def ts(self):
          df = self.data
          res = sns.lineplot(data=df)
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
          


    

          