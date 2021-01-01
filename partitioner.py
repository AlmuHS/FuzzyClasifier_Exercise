import pandas as pd
import numpy as np


class Partitioner:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def gen_partition_set(self):
        random_df = self.df.sample(frac=1)
        self.partition_set = np.array_split(random_df, 5)

        return self.partition_set
