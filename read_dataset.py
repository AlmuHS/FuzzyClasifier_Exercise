import pandas as pd
import numpy as np

def load_data(filename: str):
     df = pd.read_csv(filename)
     
     return df

def calculate_means(df: pd.DataFrame):
        return df.mean()


def calculate_label_ranges(df: pd.DataFrame, var_name: str):
        mean = mean_df[var_name]
        max_value = df[var_name].max()
        min_value = df[var_name].min()

        delta = max_value - min_value

        mid_rangemax = max_value - (max_value - mean)/2
        mid_rangemin = min_value + (mean - min_value)/2
        
        ranges_dict = {"Low": [min_value, mid_rangemin],"Medium": [mid_rangemin, mid_rangemax], "High": [mid_rangemax, max_value]}

        return ranges_dict


def set_tags(df: pd.DataFrame):
        tags = dict()

        for row in df.keys()[:-1]:
                tags[row] = calculate_label_ranges(df, row)
                
        return tags

def get_training_df(df: pd.DataFrame, types: list):
        training_set = []

        for type in types:
                rows_type = df.loc[df['Type'] == type]
                filtered_rows = rows_type[1:10]

                training_set.append(filtered_rows)

        training_df = pd.concat(training_set)    
        
        return training_df    

def select_tag_for_key(key: str, value: float, tag_range: list):
        tag_range_high = tag_range["High"]
        tag_range_medium = tag_range["Medium"]
        tag_range_low = tag_range["Low"]

        tag = ""
        
        if value >= tag_range_high[0] and value <= tag_range_high[1]:
                tag = "High"
        elif value >= tag_range_medium[0] and value <= tag_range_medium[1]:
                tag = "Medium"
        elif value >= tag_range_low[0] and value <= tag_range_low[1]:
                tag = "Low" 

        return tag


def fuzzify_dataset(df: pd.DataFrame, tags_ranges):
        keys = df.keys()
        fuzzy_df = pd.DataFrame(columns = df.columns[:-1])

        print(len(fuzzy_df.columns))

        for key in keys[:-1]:
                key_column = training_df[key]
                tag_range = tags_ranges[key]
                
                for i, value in enumerate(key_column):      
                        fuzzy_df.at[i, key] = select_tag_for_key(key, value, tag_range)

        return fuzzy_df


def get_training_rules(training_df: pd.DataFrame, tags_ranges: dict):
        keys = training_df.keys()
        rules_df = pd.DataFrame(columns = keys)

        rules_df = fuzzify_dataset(df, tags_ranges)
       
        for i, type in enumerate(training_df['Type']):
                rules_df.at[i, "Type"] = training_df.iloc[i]["Type"]
       
        return rules_df

def classify_dataset(fuzzy_df: pd.DataFrame, rules_df: pd.DataFrame):
        print(fuzzy_df.columns)
        print(rules_df.columns)
        
        
        #print(merge)
                
        


df = load_data("glass.csv")
mean_df = calculate_means(df)

tags_ranges = set_tags(df)
print(tags_ranges)

types = range(1,8)

training_df = get_training_df(df, types)
rules_training = get_training_rules(training_df, tags_ranges)

#print(rules_training)

#print(df.columns)
fuzzy_df = fuzzify_dataset(df, tags_ranges)
#print(fuzzy_df)

#classify_dataset(fuzzy_df, rules_training)
