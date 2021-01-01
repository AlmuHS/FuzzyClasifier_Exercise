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

    def calculate_asociation_degree(self, tag_range: list, tag_list: list, value: float):
        tag = tag_list[0]
        tag_range_low = tag_range["Low"]

        if len(tag_list) == 1:
            tag_range_low_left = tag_range_low[0]
            tag_range_low_right = tag_range_low[1]

            range_size = tag_range_low_right - tag_range_low_left

            distance_left = (value - tag_range_low_left)
            asociation_degree = distance_left/range_size

        else:
            min_degree = 1

            for tag1, tag2 in pairwise(tag_list):
                t_range1 = tag_range[tag1]
                t_range2 = tag_range[tag2]

                t_range1_left = t_range1[0]
                t_range2_left = t_range2[0]

                t_range1_right = t_range1[1]
                t_range2_right = t_range2[1]

                range1_size = t_range1_right - t_range1_left
                range2_size = t_range2_right - t_range2_left

                asociation_degree1 = (t_range1_right - value)/range1_size
                asociation_degree2 = (value - t_range2_left)/range2_size

                if asociation_degree1 < min_degree:
                    min_degree = asociation_degree1
                    tag = tag1

                if asociation_degree2 < min_degree:
                    min_degree = asociation_degree2
                    tag = tag2

            asociation_degree = min_degree

        return tag, asociation_degree

    def select_tag_for_key(self, value: float, tag_range: list):
        tag_range_high = tag_range["High"]
        tag_range_medium = tag_range["Medium"]
        tag_range_low = tag_range["Low"]

        tag_list = []
        tag = ""

        if self._check_range(value, tag_range_low[0], tag_range_low[1]):
            tag_list.append("Low")

        if self._check_range(value, tag_range_medium[0], tag_range_medium[1]):
            tag_list.append("Medium")

        if self._check_range(value, tag_range_high[0], tag_range_high[1]):
            tag_list.append("High")

        tag = tag_list[0]

        tag, overleap_degree = self.calculate_asociation_degree(
            tag_range, tag_list, value)

        return tag, overleap_degree

    def select_tag_for_data(self, value: float, tag_range: list):
        tag, key = self.select_tag_for_key(value, tag_range)

        return tag

    def calculate_row_overleap(self, row: pd.DataFrame):
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
            lambda x: self.calculate_row_overleap(x), axis=1)

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
