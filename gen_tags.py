import pandas as pd

class genTags:
        def __init__(self, df: pd.DataFrame):
                self.df = df

        def calculate_means(self):
                return self.df.mean()


        def calculate_tag_ranges(self, mean_df: pd.DataFrame, var_name: str):
                mean = mean_df[var_name]
                max_value = self.df[var_name].max()
                min_value = self.df[var_name].min()

                mid_rangemax = max_value - (max_value - mean)/2
                mid_rangemin = min_value + (mean - min_value)/2
                
                low_range_max = max_value - (max_value - min_value)/3   
                high_range_min = max_value - (max_value - min_value)/2
                
                ranges_dict = {"Low": [min_value, low_range_max],"Medium": [mid_rangemin, mid_rangemax], "High": [high_range_min, max_value]}

                return ranges_dict


        def set_tags(self):
                tags = dict()
                mean_df = self.calculate_means() 

                for row in self.df.keys()[:-1]:
                        tags[row] = self.calculate_tag_ranges(mean_df, row)
                        
                return tags
