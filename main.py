import pandas as pd
from rules_gen import RulesGenerator as RulesGen
from fuzzifier import Fuzzyfier as FuzGen
from gen_tags import genTags as gt
from classifier import Classifier


def load_data(filename: str):
    df = pd.read_csv(filename)

    return df


pd.set_option('display.max_rows', None)
df = load_data("glass.csv")

tags_ranges = gt(df).set_tags()

rules_gen = RulesGen(df)
best_rules_gen = rules_gen.start_rules_training()
fuzzy_data = FuzGen(df).fuzzify_data(tags_ranges)

classifier = Classifier(fuzzy_data, best_rules_gen)
classifier.classify_dataset()
TP_value, results = classifier.verify_classification()

accuraccy = TP_value/len(df)

print(accuraccy)
print(best_rules_gen)
