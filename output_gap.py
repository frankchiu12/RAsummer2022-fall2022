import pandas as pd
from datetime import datetime

output_gap_df = pd.read_excel('Greenbook_Output_Gap_DH_Web.xlsx')
column_name_list = []
for column in output_gap_df.columns:
    column_name_list.append(column)
del column_name_list[0]
row_name_list = output_gap_df['Unnamed: 0'].tolist()
new_data_list = []

for i in range(len(column_name_list)):
    try:
        column_value_list = output_gap_df[column_name_list[i]].values.tolist()
        column_name_list[i] = datetime.strptime(column_name_list[i][6:], '%y%m%d')
        year = column_name_list[i].year
        quarter = pd.Timestamp(column_name_list[i]).quarter

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

output_gap_df = pd.DataFrame(new_data_list, index = column_name_list, columns = row_name_list)
writer = pd.ExcelWriter('Greenbook_Output_Gap_Updated.xlsx', engine = 'xlsxwriter')
output_gap_df.transpose().to_excel(writer)
writer.save()

FOMC_excel = pd.ExcelFile('GBweb_Row_Format.xlsx')
CPI_df = pd.read_excel(FOMC_excel, 'gPCPI')
FOMC_GB_date_list = CPI_df['GBdate'].values.tolist()
FOMC_GB_date_list = [datetime.strptime(str(x), '%Y%m%d') for x in FOMC_GB_date_list]

gPCPI_list = []
for i in range(10):
    gPCPI_list.append('gPCPIF' + str(i))

GB_date_to_CPI = {}
for i in range(len(FOMC_GB_date_list)):
    if FOMC_GB_date_list[i] not in GB_date_to_CPI:
        GB_date_to_CPI[FOMC_GB_date_list[i]] = []
        for gPCPI in gPCPI_list:
            GB_date_to_CPI[FOMC_GB_date_list[i]].append(CPI_df[gPCPI].values.tolist()[i])

output_gap_df = output_gap_df.transpose()

def taylor_1993_equation(inflation, output_gap):
    return 1.25 + inflation + 0.5 * (inflation - 2) + 0.5 * output_gap

def taylor_1999_equation(inflation, output_gap):
    return 1.25 + inflation + 0.5 * (inflation - 2) + output_gap

date_to_taylor_1993 = {}
date_to_taylor_1999 = {}
for column in column_name_list:
    CPI_list = GB_date_to_CPI[column]
    output_gap_list = output_gap_df[column].tolist()
    output_gap_list = [x for x in output_gap_list if isinstance(x, float)]
    max_length = max(len(CPI_list), len(output_gap_list))

    if column not in date_to_taylor_1993:
        date_to_taylor_1993[column] = []
        for i in range(max_length):
            try:
                date_to_taylor_1993[column].append(taylor_1993_equation(CPI_list[i], output_gap_list[i]))
            except IndexError:
                break

    if column not in date_to_taylor_1999:
        date_to_taylor_1999[column] = []
        for i in range(max_length):
            try:
                date_to_taylor_1999[column].append(taylor_1999_equation(CPI_list[i], output_gap_list[i]))
            except IndexError:
                break

FOMC_excel = pd.ExcelFile('GBweb_Row_Format.xlsx')
CPI_df = pd.read_excel(FOMC_excel, 'gPCPI')
FOMC_GB_date_list = CPI_df['GBdate'].values.tolist()
FOMC_GB_date_list = [datetime.strptime(str(x), '%Y%m%d') for x in FOMC_GB_date_list]

print(date_to_taylor_1993)
print(date_to_taylor_1999)