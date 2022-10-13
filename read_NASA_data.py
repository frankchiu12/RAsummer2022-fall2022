import json
import pandas as pd

# change file paths
raw_json_data = json.load(open('other_data/ntrs-public-metadata_cut.json'))
raw_df = pd.DataFrame(raw_json_data)
raw_df = raw_df.transpose()
parsed_df = pd.DataFrame()

raw_df_length = len(raw_df)
for i in range(raw_df_length):
    if 1950 <= int(raw_df.iloc[i]['publications'][0]['publicationDate'][:4]) <= 1975:
        parsed_df = parsed_df.append(raw_df.iloc[i])

parsed_df.to_csv('NASA_output_1950_1975.csv', index = False)