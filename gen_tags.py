import pandas as pd


class genTags:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def calculate_column_means(self):
        return self.df.mean()

        '''
        Calculate the values range for each tag, based on dataset's row values
        Split the full ranges value in 3 subranges, one for each tag.

        Receives as input the name of the row to split in tags
        Returns a map of lists indexed by tag, with the initial and final value of each tag's range
        '''

    def calculate_tag_ranges(self, mean_df: pd.DataFrame, var_name: str):
        mean = mean_df[var_name]
        max_value = self.df[var_name].max()
        min_value = self.df[var_name].min()

        '''
        Each subrange has different width. The middle subrange is based in the mean value of the row in the dataset.
        The middle subrange can be different than the center of the range.
        '''
        mid_rangemax = max_value - (max_value - mean)/2
        mid_rangemin = min_value + (mean - min_value)/2

        '''
        To generate a little overlap, we modify the limits of "Low" and "High" subranges 
        with a variant of the middle subranges' limits functions
        '''
        low_range_max = max_value - (max_value - min_value)/3
        high_range_min = max_value - (max_value - min_value)/2

        '''
        The minimum of low range and maximum of high range, corresponds to the min and max value in the dataset
        '''
        ranges_dict = {"Low": [min_value, low_range_max], "Medium": [
            mid_rangemin, mid_rangemax], "High": [high_range_min, max_value]}

        return ranges_dict

        '''
        Set the tags for each variable of the dataset, calculating its subranges.
        Due to the context of the dataset is unknown, all variables will use the same tags: Low, Medium and High
        '''

    def set_tags(self):
        tags = dict()
        mean_df = self.calculate_column_means()

        for variable in self.df.keys()[:-1]:
            tags[variable] = self.calculate_tag_ranges(mean_df, variable)

        return tags
