import pandas as pd


class Classifier:
    def __init__(self, fuzzy_df: pd.DataFrame, rules_df: pd.DataFrame):
        self.fuzzy_df = fuzzy_df
        self.rules_df = rules_df

    def select_type(self, row: tuple):
        for i, rule in self.rules_df.iterrows():
            if tuple(rule[:-2]) == tuple(row[:-1]):
                return rule

        row['Type'] = -1
        row['Owning Degree'] = 0

        return row

    def classify_dataset(self):
        self.classified_df = self.fuzzy_df.apply(
            lambda x: self.select_type(x), axis=1)

        return self.classified_df

    def verify_classification(self):
        keys = self.classified_df.columns[:-1]
        matched = self.classified_df.loc[(self.classified_df[keys]
                                          == self.fuzzy_df[keys]).all(axis="columns")]

        TP_value = len(matched)

        return TP_value, matched
