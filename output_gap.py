import pandas as pd
from datetime import datetime

df = pd.read_excel('Greenbook_Output_Gap_DH_Web.xlsx')
column_name_list = []
for column in df.columns:
    column_name_list.append(column)
del column_name_list[0]
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
                    blank_list = []
                    for i in range(row_index):
                        blank_list.append('')
                    new_data_list.append(blank_list + column_value_list[row_index:])
                    break
    except ValueError:
        continue

df = pd.DataFrame(new_data_list, index = column_name_list, columns = row_name_list)
writer = pd.ExcelWriter('Greenbook_Output_Gap_Updated.xlsx', engine = 'xlsxwriter')
df.transpose().to_excel(writer)
writer.save()