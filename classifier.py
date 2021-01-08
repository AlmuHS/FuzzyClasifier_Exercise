import pandas as pd


class Classifier:
    def __init__(self, fuzzy_df: pd.DataFrame, rules_df: pd.DataFrame):
        self.fuzzy_df = fuzzy_df
        self.rules_df = rules_df

    def select_type(self, row: tuple):
        # row_df = pd.DataFrame(row).drop(['Type'], axis=0)
        # rules_filtered = self.rules_df.drop(['Owning Degree', 'Type'], axis=1)

        # try:
        #     match = self.rules_df[rules_filtered == row_df]
        # except:
        #     row['Type'] = -1
        #     row['Owning Degree'] = 0

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
        matched = self.fuzzy_df[self.fuzzy_df.isin(
            self.classified_df[:-1])].dropna()

        TP_value = len(matched)

        print(TP_value)

        return TP_value, matched
