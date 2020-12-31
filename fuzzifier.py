import pandas as pd


class Fuzzyfier:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _check_range(self, value: float, min: float, max: float):
        return ((value >= min) and (value <= max))

    def select_tag_for_key(self, value: float, tag_range: list):
        tag_range_high = tag_range["High"]
        tag_range_medium = tag_range["Medium"]
        tag_range_low = tag_range["Low"]

        tag_list = []
        tag = ""

        if self._check_range(value, tag_range_high[0], tag_range_high[1]):
            tag_list.append("High")

        if self._check_range(value, tag_range_medium[0], tag_range_medium[1]):
            tag_list.append("Medium")

        if self._check_range(value, tag_range_low[0], tag_range_low[1]):
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
                center_distance = (value - center_value) / \
                    (t_range_max - t_range_min)

                if(center_distance < min_center_distance):
                    min_center_distance = center_distance
                    tag = tag_

        return tag

    def fuzzify_dataset(self, tags_ranges: dict):
        keys = self.df.columns
        fuzzy_df = pd.DataFrame()

        for key in keys[:-1]:
            tag_range = tags_ranges[key]
            fuzzy_df[key] = self.df[key].apply(
                lambda x: self.select_tag_for_key(x, tag_range))

        fuzzy_df['Type'] = self.df['Type'].copy(deep=False)

        return fuzzy_df
