import pandas as pd
import gc


class Fuzzyfier:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    '''
    Calculates the owning degree of a value to a specific tag.
    Receives as parameter the discrete value, and the tag range (with the min and max of the tag)
    '''

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
    Select the best tag for a discrete value, based in its discrete value and the ranges of each tag.
    Compare the discrete value with the range of each tag, calculation the owning degree for each.
    
    Select the tag with the higher association degree. 
    '''

    def select_tag_for_value(self, value: float, tags_ranges: dict):
        max_own_degree = 0

        tag_code = {"Low": 1, "Medium": 2, "High": 3}
        best_tag = tag_code["Low"]

        for tag in ["Low", "Medium", "High"]:
            tag_range = tags_ranges[tag]

            own_degree = self.calculate_owning_degree(
                value, tag_range)

            if own_degree > max_own_degree:
                max_own_degree = own_degree
                best_tag = tag_code[tag]

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

    '''
    Select the best tag for a data example. Use the same criteria than
    the rules, but discarding the "Owning Degree" column
    '''

    def select_tag_for_data(self, value: float, tags_ranges: dict):
        tag, degree = self.select_tag_for_value(value, tags_ranges)

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
                lambda x: self.select_tag_for_value(x, tag_range))

        # Copy Type (class) column to fuzzy dataframe
        type_str = keys[-1]
        fuzzy_df[type_str] = self.df[type_str].copy(deep=False)

        # Calculate Owning Degree for each rule, and add it in a new column
        fuzzy_df = fuzzy_df.apply(
            lambda x: self.calculate_rule_owning_degree(x), axis=1)

        # Casting type to int
        fuzzy_df = fuzzy_df[:-1].astype('int8', copy=False)

        # Clean memory
        self.df = None
        gc.collect()

        return fuzzy_df

    '''
    Fuzzify a examples set, to transform it in a rules set.
    For each row, assign a fuzzy tag for each term
    '''

    def fuzzify_data(self, tags_ranges: dict):
        keys = self.df.columns

        # Create a new dataframe, setting int as default type
        fuzzy_df = pd.DataFrame(dtype='int8')

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_data(x, tag_range))

        # Copy Type (class) column to fuzzy dataframe
        type_column = keys[-1]
        fuzzy_df[type_column] = self.df[type_column].copy(deep=False)

        # Clean memory
        self.df = None
        gc.collect()

        return fuzzy_df
