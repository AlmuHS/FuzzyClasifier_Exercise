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
        t_range_right = tag_range[1]

        asociation_degree = value/t_range_right

        return asociation_degree

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

        tag_range = tags_ranges[tag]

        asociation_degree = self.calculate_asociation_degree(
            tag, value, tag_range)

        return tag, asociation_degree

    '''
    Return the best tag for a classifier example, ignoring the association degree
    '''

    def select_tag_for_data(self, value: float, tag_range: list):
        tag, asociation_degree = self.select_tag_for_key(value, tag_range)

        return tag

    '''
    Calculate the asociation degree of a rule, as the average asociation degree of its terms.
    '''

    def calculate_rule_asociation(self, row: pd.DataFrame):
        total_association = 1
        keys = row.keys()
        modified_row = row

        for key in keys:
            association = row[key][1]
            total_association += association

            modified_row[key] = row[key][0]

        modified_row['Asociation'] = total_association/len(keys)

        return modified_row

    '''
    Fuzzify a examples set, to transform it in a fuzzy rules set.
    For each example, assign a fuzzy tag for each term, and calculates a association degree
    Once fuzzified all examples, calculate the association degree of each rule, and add it in a new column
    '''

    def fuzzify_rules(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        # Fuzzify terms, and put each tag together its asociation degree
        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_key(x, tag_range))

        # Remove association degree of variables columns, and generate a new column with the weight of this key
        fuzzy_df = fuzzy_df.apply(
            lambda x: self.calculate_rule_asociation(x), axis=1)

        # Copy the Type clasification in each rule from the initial examples set
        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        return fuzzy_df

    '''
    Fuzzify a dataset, to transform it in a classification set.
    Makes the same than fuzzify_rules, but ignoring the association degree in the final dataset
    '''

    def fuzzify_data(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_data(x, tag_range))

        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        return fuzzy_df
