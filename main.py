import pandas as pd

from rules_gen import RulesGenerator as RulesGen


def load_data(filename: str):
    df = pd.read_csv(filename)

    return df


pd.set_option('display.max_rows', None)
df = load_data("glass.csv")

rules_gen = RulesGen(df)
rules_gen.start_rules_training()
