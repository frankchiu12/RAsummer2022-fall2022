from typing import Type
import pandas as pd
from datetime import datetime
import pygsheets

sheet = pygsheets.authorize(service_account_file = 'write_into_google_sheet.json').open('Summer RA')
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
    try:
        return 1.25 + inflation + 0.5 * (inflation - 2) + 0.5 * output_gap
    except TypeError:
        return ''

def taylor_1999_equation(inflation, output_gap):
    try:
        return 1.25 + inflation + 0.5 * (inflation - 2) + output_gap
    except TypeError:
        return ''

date_to_taylor_1993 = {}
date_to_taylor_1999 = {}
for column in column_name_list:
    CPI_list = GB_date_to_CPI[column]
    column = datetime.strftime(column, '%m/%d/%Y')
    output_gap_list = output_gap_df[column].tolist()
    output_gap_list = [x for x in output_gap_list if isinstance(x, float)]
    max_length = max(len(CPI_list), len(output_gap_list))

    if column not in date_to_taylor_1993:
        date_to_taylor_1993[column] = []
        for i in range(max_length):
            try:
                if pd.isna(CPI_list[i]):
                    CPI_list[i] = ''
                if pd.isna(output_gap_list[i]):
                    output_gap_list[i] = ''
                date_to_taylor_1993[column].append(taylor_1993_equation(CPI_list[i], output_gap_list[i]))
            except IndexError:
                break

    if column not in date_to_taylor_1999:
        date_to_taylor_1999[column] = []
        for i in range(max_length):
            try:
                if pd.isna(CPI_list[i]):
                    CPI_list[i] = ''
                if pd.isna(output_gap_list[i]):
                    output_gap_list[i] = ''
                date_to_taylor_1999[column].append(taylor_1999_equation(CPI_list[i], output_gap_list[i]))
            except IndexError:
                break

FOMC_excel = pd.ExcelFile('GBweb_Row_Format.xlsx')
CPI_df = pd.read_excel(FOMC_excel, 'gPCPI')
FOMC_GB_date_list = CPI_df['GBdate'].values.tolist()
FOMC_GB_date_list = [datetime.strptime(str(x), '%Y%m%d') for x in FOMC_GB_date_list]

def write_to_google_sheets(dictionary, worksheet):
    date_list = ['Date']
    ffr_0 = ['FFR0']
    ffr_1 = ['FFR1']
    ffr_2 = ['FFR2']
    ffr_3 = ['FFR3']
    ffr_4 = ['FFR4']
    ffr_5 = ['FFR5']
    ffr_6 = ['FFR6']
    ffr_7 = ['FFR7']
    ffr_8 = ['FFR8']
    ffr_9 = ['FFR9']

    for date, predicted_ffr in dictionary.items():
        date_list.append(date)
        ffr_0.append(predicted_ffr[0])
        ffr_1.append(predicted_ffr[1])
        ffr_2.append(predicted_ffr[2])
        ffr_3.append(predicted_ffr[3])
        ffr_4.append(predicted_ffr[4])
        ffr_5.append(predicted_ffr[5])
        ffr_6.append(predicted_ffr[6])
        ffr_7.append(predicted_ffr[7])
        ffr_8.append(predicted_ffr[8])
        ffr_9.append(predicted_ffr[9])

    worksheet = sheet.add_worksheet(worksheet, rows = 168, cols = 11)
    worksheet.update_col(1, date_list)
    worksheet.update_col(2, ffr_0)
    worksheet.update_col(3, ffr_1)
    worksheet.update_col(4, ffr_2)
    worksheet.update_col(5, ffr_3)
    worksheet.update_col(6, ffr_4)
    worksheet.update_col(7, ffr_5)
    worksheet.update_col(8, ffr_6)
    worksheet.update_col(9, ffr_7)
    worksheet.update_col(10, ffr_8)
    worksheet.update_col(11, ffr_9)

write_to_google_sheets(date_to_taylor_1993, 'taylor_1993_projections')
write_to_google_sheets(date_to_taylor_1999, 'taylor_1999_projections')