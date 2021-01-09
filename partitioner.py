import pandas as pd
import numpy as np


class Partitioner:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    '''
    Generates a partition set, splitting the examples set in 5 random partitions.
    
    '''

    def gen_partition_set(self):

        # Sort the dataframe in a random way
        random_df = self.df.sample(frac=1)

        # Split the randomed dataframe in 5 partitions  
        self.partition_set = np.array_split(random_df, 5)

        return self.partition_set
