import pandas as pd
from fuzzifier import Fuzzyfier as FuzGen
from gen_tags import genTags as gt
from partitioner import Partitioner as Part
from classifier import Classifier


class RulesGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_training_rules(self, training_df: pd.DataFrame, tags_ranges: dict):
        fuzzifier = FuzGen(training_df)
        rules_df = fuzzifier.fuzzify_dataset(tags_ranges)

        return rules_df

    def gen_rules_set(self, training_set: list, tags_ranges: dict):
        rules_set = []

        for training_df in training_set:
            rules_df = self.get_training_rules(training_df, tags_ranges)

            rules_set.append(rules_df)

        return rules_set

    def start_rules_training(self):
        gen_tags = gt(self.df)
        tags_ranges = gen_tags.set_tags()

        parts_gen = Part(self.df)
        parts_gen.gen_partition_set()
        test_df = parts_gen.get_test_df()

        training_set = parts_gen.get_training_set()
        rules_set = self.gen_rules_set(training_set, tags_ranges)

        print(len(rules_set))

        fuzzifier = FuzGen(test_df)
        fuzzy_df = fuzzifier.fuzzify_dataset(tags_ranges)

        best_accuraccy = 0
        best_rulesset = 0

        for i, rules_df in enumerate(rules_set):
            classifier = Classifier(fuzzy_df, rules_df)
            classifier.classify_dataset()

            TP_value = classifier.verify_classification()
            accuraccy = (TP_value / len(fuzzy_df))

            if accuraccy > best_accuraccy:
                best_accuraccy = accuraccy
                best_rulesset = i

        return rules_set[best_rulesset]
