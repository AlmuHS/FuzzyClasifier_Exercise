import pandas as pd
from more_itertools import pairwise


class Fuzzyfier:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def calculate_owning_degree(self, value: float, tag_range: list):
        own_degree = 0
        tag_limit_left = tag_range[0]
        tag_limit_right = tag_range[1]
        middle_value = tag_limit_right/2

        if value < tag_limit_left:
            own_degree = 0
        elif value > tag_limit_left and value <= middle_value:
            own_degree = (value - tag_limit_left) / \
                (middle_value - tag_limit_left)
        elif value > middle_value and value < tag_limit_right:
            own_degree = (tag_limit_right - value) / \
                (tag_limit_right - middle_value)
        elif value > tag_limit_right:
            own_degree = 0

        return own_degree

    '''
    Select the best tag for a key, based in its discrete value and the ranges of each tag.
    Compare the discrete value with the range of each tag, calculation the owning degree for each.
    
    Select the tag with the higher association degree. 
    '''

    def select_tag_for_rule(self, value: float, tags_ranges: dict):
        max_own_degree = 0
        best_tag = "Low"

        for tag in ["Low", "Medium", "High"]:
            tag_range = tags_ranges[tag]

            own_degree = self.calculate_owning_degree(
                value, tag_range)

            if own_degree > max_own_degree:
                max_own_degree = own_degree
                best_tag = tag

        return best_tag, max_own_degree

    def calculate_rule_owning_degree(self, rule: pd.DataFrame):
        total_own_degree = 0

        for column in rule.keys()[:-1]:
            term = rule[column]
            tag = term[0]
            own_degree = term[1]

            total_own_degree += own_degree
            rule[column] = tag

        rule["Owning Degree"] = total_own_degree

        return rule

    def select_tag_for_data(self, value: float, tags_ranges: dict):
        tag, degree = self.select_tag_for_rule(value, tags_ranges)

        return tag

    '''
    Fuzzify a examples set, to transform it in a rules set.
    For each row, assign a fuzzy tag for each term
    '''

    def fuzzify_rules(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_rule(x, tag_range))

        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        fuzzy_df = fuzzy_df.apply(
            lambda x: self.calculate_rule_owning_degree(x), axis=1)

        return fuzzy_df

    '''
    Fuzzify a examples set, to transform it in a rules set.
    For each row, assign a fuzzy tag for each term
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
