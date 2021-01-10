import pandas as pd
import gc
from rules_gen import RulesGenerator as RulesGen
from fuzzifier import Fuzzyfier as FuzGen
from gen_tags import genTags as gt
from classifier import Classifier


def load_data(filename: str):
    df = pd.read_csv(filename)

    return df


gc.enable()

pd.set_option('display.max_rows', None)
#df = load_data("glass.csv")
df = load_data("covtype.csv")

tags_ranges = gt(df).set_tags()

rules_gen = RulesGen(df)
best_rules_gen = rules_gen.start_rules_training()
fuzzy_data = FuzGen(df).fuzzify_data(tags_ranges)

classifier = Classifier(fuzzy_data, best_rules_gen)
classifier.classify_dataset()
TP_value, results = classifier.verify_classification()

accuraccy = TP_value/len(df)

print(f"Full dataset accuraccy: {accuraccy}")
print(f"Minimal rules set: \n{best_rules_gen}")
