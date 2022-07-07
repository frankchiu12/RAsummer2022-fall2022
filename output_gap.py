import pandas as pd
from datetime import datetime

df = pd.read_excel('Greenbook_Output_Gap_DH_Web.xlsx')

column_name_list = []
for column in df.columns:
    column_name_list.append(column)

row_name_list = df['Unnamed: 0'].tolist()

new_data_list = []
for column_name in column_name_list:
    try:
        column_value_list = df[column_name].values.tolist()
        column_name = datetime.strptime(column_name[6:], '%y%m%d')
        year = column_name.year
        quarter = pd.Timestamp(column_name).quarter

        for row_name in row_name_list:
            if int(row_name.split(':')[0]) >= year:
                if int(row_name.split(':')[1]) >= quarter:
                    row_index = row_name_list.index(row_name)
                    new_data_list.append(column_value_list[row_index:])
                    break
    except ValueError:
        continue

print(new_data_list)