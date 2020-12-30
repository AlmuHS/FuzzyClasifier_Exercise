import pandas as pd
import numpy as np

def load_data(filename: str):
     df = pd.read_csv(filename)
     
     return df

def calculate_means(df: pd.DataFrame):
        return df.mean()


def calculate_tag_ranges(df: pd.DataFrame, var_name: str):
        mean = mean_df[var_name]
        max_value = df[var_name].max()
        min_value = df[var_name].min()

        mid_rangemax = max_value - (max_value - mean)/2
        mid_rangemin = min_value + (mean - min_value)/2
        
        #high_range_min = min_value + (max_value - mid_rangemax/2)
        
        low_range_max = max_value - (max_value - min_value)/3   
        high_range_min = max_value - (max_value - min_value)/2
        
        ranges_dict = {"Low": [min_value, low_range_max],"Medium": [mid_rangemin, mid_rangemax], "High": [high_range_min, max_value]}

        return ranges_dict


def set_tags(df: pd.DataFrame):
        tags = dict()

        for row in df.keys()[:-1]:
                tags[row] = calculate_tag_ranges(df, row)
                
        return tags

def check_range(value: float, min: float, max: float):
        return ((value >= min) and (value <= max))


def select_tag_for_key(value: float, tag_range: list):
        tag_range_high = tag_range["High"]
        tag_range_medium = tag_range["Medium"]
        tag_range_low = tag_range["Low"]

        tag_list = []
        tag = ""
        
        if check_range(value, tag_range_high[0], tag_range_high[1]):
                tag_list.append("High")
        
        if check_range(value, tag_range_medium[0], tag_range_medium[1]):
                tag_list.append("Medium")
        
        if check_range(value, tag_range_low[0], tag_range_low[1]):
                tag_list.append("Low")
        
        if len(tag_list) == 1:
                tag = tag_list[0]
        else:
                min_center_distance = 100000000000000000000000.0

                tag = tag_list[0]

                for tag_ in tag_list:
                        t_range = tag_range[tag_]
                        t_range_min = t_range[0]
                        t_range_max = t_range[1]
                
                        center_value = (t_range_max-t_range_min)/2
                        center_distance = value - center_value
                
                        if(center_distance < min_center_distance):
                                min_center_distance = center_distance
                                tag = tag_
                
        return tag


def fuzzify_dataset(df: pd.DataFrame, tags_ranges: dict):
        keys = df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
                tag_range = tags_ranges[key]
                fuzzy_df[key] = df[key].apply(lambda x: select_tag_for_key(x, tag_range))
                
        return fuzzy_df

def get_training_df(df: pd.DataFrame, types: list):
        training_set = []

        for type in types:   
                rows_type = df.loc[df['Type'] == type]
        
                filtered_rows = rows_type#[1:10]

                training_set.append(filtered_rows)

        training_df = pd.concat(training_set) 
        
        return training_df    

def get_training_rules(df: pd.DataFrame, tags_ranges: dict, types: list):
        keys = df.keys()

        training_df = get_training_df(df, types) 
        rules_df = fuzzify_dataset(training_df, tags_ranges)
       
        rules_df['Type'] = training_df['Type'].copy(deep=False)
       
        rules_df.drop_duplicates(keep=False, inplace=True)
       
        return rules_df

def classify_dataset(fuzzy_df: pd.DataFrame, rules_df: pd.DataFrame):
        merge_in  = pd.merge(fuzzy_df, rules_df, how = 'outer', on = list(fuzzy_df.columns))
        
        for i, row in fuzzy_df.iterrows():
                match_list = []
        
                for j, rule in rules_df.iterrows():                
                        if tuple(row) == tuple(rule[:-1]):
                                match_list.append(rule)
                                #print(f"{tuple(row)}\n{tuple(rule)}\n\n")
                
                print(f"row {tuple(row)}: {len(match_list)} matches")
                if len(match_list) > 1:
                        print(match_list)
        
        return merge_in


pd.set_option('display.max_rows', None)


df = load_data("glass.csv")
mean_df = calculate_means(df)

tags_ranges = set_tags(df)
print(tags_ranges)

types = range(1,8)
rules_training = get_training_rules(df, tags_ranges, types)
print(rules_training)

fuzzy_df = fuzzify_dataset(df, tags_ranges)
print(fuzzy_df)

classified_df = classify_dataset(fuzzy_df, rules_training)
print(classified_df)
