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

    def calculate_asociation_degree(self, tag: str, value: float, tag_range: list):
        t_range_left = tag_range[0]
        t_range_right = tag_range[1]

        t_range_size = t_range_right - t_range_left

        asociation_degree = (value - t_range_left)/t_range_size

        return asociation_degree

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

        tag_range = tags_ranges[tag]

        asociation_degree = self.calculate_asociation_degree(
            tag, value, tag_range)

        return tag, asociation_degree

    def select_tag_for_data(self, value: float, tag_range: list):
        tag, key = self.select_tag_for_key(value, tag_range)

        return tag

    def calculate_row_weight(self, row: pd.DataFrame):
        total_overleap = 1
        keys = row.keys()
        modified_row = row

        for key in keys:
            overleap = row[key][1]
            total_overleap *= overleap

            modified_row[key] = row[key][0]

        modified_row['Asociation'] = total_overleap

        return modified_row

    def fuzzify_rules(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_key(x, tag_range))

        fuzzy_df = fuzzy_df.apply(
            lambda x: self.calculate_row_weight(x), axis=1)

        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        return fuzzy_df

    def fuzzify_data(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_data(x, tag_range))

        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        return fuzzy_df
