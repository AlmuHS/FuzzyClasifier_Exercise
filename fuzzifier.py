import pandas as pd
from more_itertools import pairwise


class Fuzzyfier:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    '''
    Check if a single value exists in a certain range
    Receives as input the two limits of the range, and the value to check
    Returns True if the number exists in the range, False if not
    '''

    def _check_range(self, value: float, min: float, max: float):
        return ((value >= min) and (value <= max))

    '''
    Select the best tag for a key, based in its discrete value and the ranges of each tag.
    Compare the discrete value with the range of each tag, finding the minimal tag in which this value matches.

    For the tag selected, calculates a asociation degree,
    which measure the similarity between the discrete value and the tag selected
    '''

    def select_tag_for_key(self, value: float, tags_ranges: list):
        tag_range_high = tags_ranges["High"]
        tag_range_medium = tags_ranges["Medium"]
        tag_range_low = tags_ranges["Low"]

        tag = "Low"

        if self._check_range(value, tag_range_low[0], tag_range_low[1]):
            tag = "Low"

        if self._check_range(value, tag_range_medium[0], tag_range_medium[1]):
            tag = "Medium"

        if self._check_range(value, tag_range_high[0], tag_range_high[1]):
            tag = "High"

        return tag

    '''
    Fuzzify a dataset, to transform it in a classification set. 
    For each row, assign a fuzzy tag for each term
    '''

    def fuzzify_data(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_key(x, tag_range))

        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        return fuzzy_df
