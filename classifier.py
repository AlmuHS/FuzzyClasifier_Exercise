import pandas as pd


class Classifier:
    def __init__(self, fuzzy_df: pd.DataFrame, rules_df: pd.DataFrame):
        self.fuzzy_df = fuzzy_df
        self.rules_df = rules_df

    def select_type(self, row: tuple):
        for i, rule in self.rules_df.iterrows():
            if tuple(row[:-1]) == tuple(rule[:-1]):
                return rule

        row['Type'] = -1
        return row

    def classify_dataset(self):
        self.classified_df = self.fuzzy_df.apply(
            lambda x: self.select_type(x), axis=1)

        return self.classified_df

    def verify_classification(self):

        merge = pd.merge(self.fuzzy_df, self.classified_df,
                         how='left', on=list(self.fuzzy_df.columns), indicator='Exist').loc[lambda x: x['Exist'] != 'both']

        # print(merge)
        TP_value = len(merge)

        print(TP_value)

        return TP_value
