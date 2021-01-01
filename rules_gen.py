import pandas as pd
from fuzzifier import Fuzzyfier as FuzGen
from gen_tags import genTags as gt
from partitioner import Partitioner as Part
from classifier import Classifier


class RulesGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_initial_rules(self, training_df: pd.DataFrame, tags_ranges: dict):
        fuzzifier = FuzGen(training_df)
        rules_df = fuzzifier.fuzzify_rules(tags_ranges)

        return rules_df

    def learn_rules(self, training_df: pd.DataFrame, tags_ranges: dict):
        examples_set = self.get_initial_rules(training_df, tags_ranges)
        examples_set.drop_duplicates(inplace=True, subset=self.df.columns)

        dup_rules = pd.merge(examples_set, examples_set, how='inner',
                             on=list(self.df.columns))

        examples_set.drop('Asociation', inplace=True, axis=1)
       # print(dup_rules)

        # min_overleap_set = examples_set.groupby(
        #     list(examples_set.columns[:-2]))[['Overleap']].min()

        # print(min_overleap_set)

        return examples_set

    def start_rules_training(self):
        gen_tags = gt(self.df)
        tags_ranges = gen_tags.set_tags()

        parts_gen = Part(self.df)
        partition_set = parts_gen.gen_partition_set()

        best_accuraccy = 0
        best_rulesset = pd.DataFrame()

        for i in range(0, len(partition_set)-1):
            test_set = partition_set[i]
            training_set = partition_set.copy()
            training_set.pop(i)

            training_df = pd.concat(training_set)

            fuzzifier = FuzGen(test_set)
            test_df = fuzzifier.fuzzify_data(tags_ranges)

            rules_df = self.learn_rules(training_df, tags_ranges)

            classifier = Classifier(test_df, rules_df)
            classifier.classify_dataset()

            TP_value = classifier.verify_classification()
            accuraccy = (TP_value / len(test_df))

            print(accuraccy)

            if accuraccy > best_accuraccy:
                best_accuraccy = accuraccy
                best_rulesset = rules_df

        return best_rulesset
