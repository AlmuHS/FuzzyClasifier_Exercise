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

    def learn_rules(self, training_df: pd.DataFrame, tags_ranges: dict, initial=True):

        if not initial:
            training_df = self.get_initial_rules(training_df, tags_ranges)

        best_rules_df = pd.DataFrame(columns=training_df.columns[:-1])

        '''
        Select the rules most repeated in the examples set
        Group the rules which match in all their terms and, for each of them, select the classtype most repeated for this group
        '''
        for values, dup_terms_sg in training_df.groupby(training_df.columns.tolist()[:-2], as_index=False):

            max_repeat = 0
            max_degree = 0
            best_rule = type(dup_terms_sg)

            '''
            For each group of rules with same predecesor terms, select the class most repeated in its rules subgroup
            '''

            for dup_types_val, dup_types_sg in dup_terms_sg.groupby(training_df.columns.tolist(), as_index=False):
                # if dup_types_val[-1] > max_degree:
                #     max_degree = dup_types_val[-1]
                #     best_rule = dup_types_sg

                num_repeat = len(dup_types_sg)

                if num_repeat > max_repeat:
                    max_repeat = num_repeat
                    best_rule = dup_terms_sg[:-1]

            best_rules_df = pd.concat([best_rules_df, best_rule])

            # print(best_rules_df)

        return best_rules_df

    def start_rules_training(self):

        # Generate the tags for the values range
        gen_tags = gt(self.df)
        tags_ranges = gen_tags.set_tags()

        # Split the dataset in 5 random partitions
        parts_gen = Part(self.df)
        partition_set = parts_gen.gen_partition_set()

        # Initialize the best rulesset using full dataset
        best_rulesset = pd.DataFrame()
        best_rulesset = self.get_initial_rules(self.df, tags_ranges)

        # Train the rules with all posible combinations of training and test partitions
        for i in range(0, len(partition_set) - 1):

            # Select the partition for the test set, using the index of the loop
            test_set = partition_set[i]

            # Select the partitions for training set, removing test partition from a copy of the partitions list
            training_set = partition_set.copy()
            training_set.pop(i)  # Remove test partition from training_set

            # Fuzzify the data from the test set
            fuzzifier = FuzGen(test_set)
            test_df = fuzzifier.fuzzify_data(tags_ranges)

            '''
            Deal each training set with the rules set, to get the best rules set.
            In each iteration, merge the matched rules with the previous rules set
            '''
            for j, training_df in enumerate(training_set):

                # Filter the best rules, removing repeated antecesors
                rules_df = self.learn_rules(best_rulesset, tags_ranges)

                # Fuzzify training partition
                fuzzifier = FuzGen(training_df)
                fuzzy_df = fuzzifier.fuzzify_data(tags_ranges)

                # Deal the new rules set to the training partition
                classifier = Classifier(fuzzy_df, rules_df)
                classifier.classify_dataset()

                # Check results of classification: matched rules and positives rate
                TP_value, matched_rules = classifier.verify_classification()

                # Concatenate the matched rules to the current best rules set
                #best_rulesset = pd.concat([best_rulesset, matched_rules])
                # print(matched_rules)

                best_rulesset = matched_rules
                # best_rulesset = pd.merge(
                #    best_rulesset, matched_rules, how='right')

            # Try to classify the test set with the rules set get from training
            classifier = Classifier(test_df, best_rulesset)
            classifier.classify_dataset()

            # Check classification results
            TP_value, matched_rules = classifier.verify_classification()

            # Calculate accuraccy
            accuraccy = (TP_value / len(test_df))
            best_rulesset = pd.concat([best_rulesset, matched_rules])

            # print(best_rulesset)

            print(accuraccy)

        return best_rulesset
