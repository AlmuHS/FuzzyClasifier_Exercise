import pandas as pd
import gc
from fuzzifier import Fuzzyfier as FuzGen
from gen_tags import genTags as gt
from partitioner import Partitioner as Part
from classifier import Classifier


class RulesGenerator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        gc.enable()

    '''
    Get a initial rules set, fuzzifying a examples set
    '''

    def get_initial_rules(self, examples_df: pd.DataFrame, tags_ranges: dict):
        fuzzifier = FuzGen(examples_df)
        rules_df = fuzzifier.fuzzify_rules(tags_ranges)

        return rules_df

    '''
    Calculate the Certainty Degree of a rule, based in the Owning Degree of the rules with the
    same predecesors
    '''

    def _calculate_certainty_degree(self, rule: pd.DataFrame, rules_gr: pd.DataFrame):
        own_degree_class = 0

        # Sum the Owning Degree of all rules with same predecesors and type
        for i, rule_example in rules_gr.iterrows():
            if tuple(rule_example[:-1]) == tuple(rule[:-1]):
                own_degree_class += rule_example['Owning Degree']

        # Sum the Owning Degree of all rules with same predecesors (ignoring type)
        own_degree_wo_class = rules_gr['Owning Degree'].sum()

        # Calculate the Certain Degree, dividing a sum with the another
        certain_degree = own_degree_class/own_degree_wo_class

        # Add a new column with the certain degree
        rule["Certain Degree"] = certain_degree

        return rule

    '''
    From a rules set, select the best rules; selecting a unique rule for each predecesors set
    '''

    def reduce_rules(self, rules_df: pd.DataFrame, tags_ranges: dict, initial=True):

        if not initial:
            rules_df = self.get_initial_rules(rules_df, tags_ranges)

        best_rules_df = pd.DataFrame(columns=rules_df.columns)

        '''
        Select the rules most repeated in the examples set
        Group the rules which match in all their predecesors and, for each of them, select the rule with highest certain degree
        '''
        for values, dup_terms_sg in rules_df.groupby(rules_df.columns.tolist()[:-2], as_index=False):

            # Calculate the Certain Degree for each rule of the group
            certain_rules = dup_terms_sg.apply(
                lambda x: self._calculate_certainty_degree(x, dup_terms_sg), axis=1)

            # Select the rule with maximum Certain Degree
            max_certain = certain_rules["Certain Degree"].max()
            best_rule = certain_rules[certain_rules["Certain Degree"]
                                      == max_certain].iloc[0]

            certain_rules = None

            # Add the selected rule to the best rules set. Remove the Certain Degree column before add the rule
            best_rules_df = best_rules_df.append(
                best_rule.drop(['Certain Degree']))

        # call to garbage collector, to clean unused memory
        gc.collect()
        rules_df = None

        return best_rules_df

    '''
    Using cross validation, generates a reduced rules set.

    Split the examples set in 5 partitions: 4 for training, 1 for test.
    Starting with the full examples set as rules set, execute 4 iterations: one for each training set
    dealing each training set with the rules set.

    In each iteration, recover the matched rules to feedback the rules set. Finally, the rules set is reduced, 
    to remove the duplicated rules, and dealed with the test set. 

    This process is repeated 4 times, selecting a different partition as test set in each.
    The training set will be updated too, using the rest of partitions which are not the test set.
    After each deal with test set, the accuraccy is calculated and showed by screen.

    Returns the minimal rules set, got after all iterations
    '''

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

        # Set original dataframe to None, to free memory
        self.df = None

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

            # Set to None to free memory
            test_set = None

            '''
            Deal each training set with the rules set, to get the best rules set.
            In each iteration, accumulate the matched rules to the previous rules set.

            This will allows to distinct the best rules, which have been matched more times
            '''
            for training_df in training_set:
                # Fuzzify training partition
                fuzzifier = FuzGen(training_df)
                fuzzy_df = fuzzifier.fuzzify_data(tags_ranges)

                # Deal the new rules set to the training partition
                classifier = Classifier(fuzzy_df, best_rulesset)
                classifier.classify_dataset()

                # Check results of classification: matched rules and positives rate
                TP_value, matched_rules = classifier.verify_classification()

                # Concatenate the matched rules to the current best rules set
                best_rulesset = pd.concat([best_rulesset, matched_rules])

                # Set to None to free memory
                matched_rules = None

                # Call to garbage collector, to clean unused memory
                gc.collect()

            '''
            Once get the matched rules over the initial set, test the rules set over the test partition
            Before this, apply a filter to select only a rule for each antecesors set, based in the matches
            got from the training
            '''

            # Filter the best rules, removing repeated antecesors
            best_rulesset = self.reduce_rules(best_rulesset, tags_ranges)
            #self.reduce_rules(best_rulesset, tags_ranges)

            # Try to classify the test set with the rules set get from training
            classifier = Classifier(test_df, best_rulesset)
            classifier.classify_dataset()

            # Check classification results
            TP_value, matched_rules = classifier.verify_classification()

            # Set to None to free memory
            matched_rules = None

            # Calculate accuraccy, as the division between the positives rate (matches) and the length of test set
            accuraccy = (TP_value / len(test_df))

            print(f"Test {i} accuraccy: {accuraccy}")

            # Call to garbage collector, to clean unused memory
            gc.collect()

        print(f"Lenght of minimal rules set: {len(best_rulesset)}")

        return best_rulesset
