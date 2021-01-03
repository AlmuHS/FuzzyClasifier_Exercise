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
        rules_df = fuzzifier.fuzzify_data(tags_ranges)

        return rules_df

    def learn_rules(self, training_df: pd.DataFrame, tags_ranges: dict):
        #training_df = self.get_initial_rules(training_df, tags_ranges)

        best_rules_df = pd.DataFrame(columns=training_df.columns)

        '''
        Select the rules most repeated in the examples set
        Group the rules which match in all their terms and, for each of them, select the classtype most repeated for this group
        '''
        for values, dup_terms_sg in training_df.groupby(training_df.columns.tolist()[:-1], as_index=False):

            max_repeat = 0
            best_rule = type(dup_terms_sg)

            '''
            For each group of rules with same predecesor terms, select the class most repeated in its rules subgroup
            '''

            for values2, dup_types_sg in dup_terms_sg.groupby(training_df.columns.tolist(), as_index=False):
                num_repeat = len(dup_types_sg)

                if num_repeat > max_repeat:
                    max_repeat = num_repeat
                    best_rule = dup_terms_sg

            best_rules_df = pd.concat([best_rules_df, best_rule])

        return best_rules_df

    def start_rules_training(self):
        gen_tags = gt(self.df)
        tags_ranges = gen_tags.set_tags()

        parts_gen = Part(self.df)
        partition_set = parts_gen.gen_partition_set()

        best_accuraccy = 0
        best_rulesset = pd.DataFrame()
        best_rulesset = self.get_initial_rules(self.df, tags_ranges)

        for i in range(0, len(partition_set)-1):
            test_set = partition_set[i]
            training_set = partition_set.copy()
            training_set.pop(i)  # Remove test partition from training_set

            training_df = pd.concat(training_set)

            fuzzifier = FuzGen(test_set)
            test_df = fuzzifier.fuzzify_data(tags_ranges)

            rules_df = self.learn_rules(best_rulesset, tags_ranges)

            classifier = Classifier(training_df, rules_df)
            classifier.classify_dataset()

            TP_value, matched_rules = classifier.verify_classification()
            best_rulesset = pd.concat([best_rulesset, matched_rules])

            classifier = Classifier(test_df, best_rulesset)
            classifier.classify_dataset()

            TP_value, matched_rules = classifier.verify_classification()
            accuraccy = (TP_value / len(test_df))

            print(accuraccy)

            if accuraccy > best_accuraccy:
                best_accuraccy = accuraccy

        return best_rulesset
