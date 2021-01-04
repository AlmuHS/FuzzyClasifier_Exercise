import pandas as pd


class Classifier:
    def __init__(self, fuzzy_df: pd.DataFrame, rules_df: pd.DataFrame):
        self.fuzzy_df = fuzzy_df
        self.rules_df = rules_df

    def select_type(self, row: tuple):
        for i, rule in self.rules_df.iterrows():
            if tuple(row[:-1]) == tuple(rule[:-2]):
                return rule

        row['Type'] = -1
        return row

    def classify_dataset(self):
        self.classified_df = self.fuzzy_df.apply(
            lambda x: self.select_type(x), axis=1)

        return self.classified_df

    def verify_classification(self):

        matched = self.fuzzy_df[self.fuzzy_df.isin(
            self.classified_df)].dropna()

        TP_value = len(matched)

        return TP_value, matched
