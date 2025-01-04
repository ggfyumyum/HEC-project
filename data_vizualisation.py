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
    
    


    

          