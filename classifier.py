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

        # matched = self.fuzzy_df[self.fuzzy_df.isin(
        #     self.classified_df)].dropna()

        # TP_value = len(matched)

        merge = pd.merge(self.fuzzy_df, self.classified_df,
                         how='left', on=list(self.fuzzy_df.columns), indicator='Exist').loc[lambda x:x['Exist'] != 'both']

        matched = pd.merge(self.fuzzy_df, self.classified_df,
                           how='left', on=list(self.fuzzy_df.columns), indicator='Exist').loc[lambda x:x['Exist'] == 'both']

        del matched['Exist']

        TP_value = len(self.fuzzy_df) - len(merge)

        return TP_value, matched
