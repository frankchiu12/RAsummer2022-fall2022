import pandas as pd
from datetime import datetime
import pygsheets
import matplotlib.pyplot as plt

sheet = pygsheets.authorize(service_account_file = 'write_into_google_sheet.json').open('Summer RA')
output_gap_df = pd.read_excel('Greenbook_Output_Gap_DH_Web.xlsx')
meeting_date_list = []
for meeting_date in output_gap_df.columns:
    meeting_date_list.append(meeting_date)
del meeting_date_list[0]
year_quarter_list = output_gap_df['Unnamed: 0'].tolist()

data_list = []
for i in range(len(meeting_date_list)):
    column_data_list = output_gap_df[meeting_date_list[i]].values.tolist()
    meeting_date_list[i] = datetime.strptime(meeting_date_list[i][6:], '%y%m%d')
    year = meeting_date_list[i].year
    quarter = pd.Timestamp(meeting_date_list[i]).quarter

    for year_quarter in year_quarter_list:
        if int(year_quarter.split(':')[0]) >= year:
            if int(year_quarter.split(':')[1]) >= quarter:
                row_index = year_quarter_list.index(year_quarter)
                blank_list = []
                for i in range(row_index):
                    blank_list.append('')
                data_list.append(blank_list + column_data_list[row_index:])
                break

output_gap_df = pd.DataFrame(data_list, index = meeting_date_list, columns = year_quarter_list)
writer = pd.ExcelWriter('Greenbook_Output_Gap_Updated.xlsx', engine = 'xlsxwriter')
output_gap_df.transpose().to_excel(writer)
writer.save()

FOMC_excel = pd.ExcelFile('GBweb_Row_Format.xlsx')
CPI_df = pd.read_excel(FOMC_excel, 'gPCPI')
FOMC_GB_date_list = [datetime.strptime(str(x), '%Y%m%d') for x in CPI_df['GBdate'].values.tolist()]

gPCPI_list = []
for i in range(10):
    gPCPI_list.append('gPCPIF' + str(i))

GB_date_to_CPI = {}
for i in range(len(FOMC_GB_date_list)):
    if FOMC_GB_date_list[i] not in GB_date_to_CPI:
        GB_date_to_CPI[FOMC_GB_date_list[i]] = []
        for gPCPI in gPCPI_list:
            GB_date_to_CPI[FOMC_GB_date_list[i]].append(CPI_df[gPCPI].values.tolist()[i])

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

def inertial_taylor_1999_equation(inflation, output_gap, prev_ffr):
    try:
        return 0.85 * prev_ffr + 0.15 * (1.25 + inflation + 0.5 * (inflation - 2) + output_gap)
    except TypeError:
        return ''

date_to_taylor_1993 = {}
date_to_taylor_1999 = {}
output_gap_df = output_gap_df.transpose()
for meeting_date in meeting_date_list:
    CPI_list = GB_date_to_CPI[meeting_date]
    meeting_date = datetime.strftime(meeting_date, '%m/%d/%Y')
    output_gap_list = [x for x in output_gap_df[meeting_date].tolist() if isinstance(x, float)]
    max_length = max(len(CPI_list), len(output_gap_list))

    if meeting_date not in date_to_taylor_1993:
        date_to_taylor_1993[meeting_date] = []
        for i in range(max_length):
            try:
                if pd.isna(CPI_list[i]):
                    CPI_list[i] = ''
                if pd.isna(output_gap_list[i]):
                    output_gap_list[i] = ''
                date_to_taylor_1993[meeting_date].append(taylor_1993_equation(CPI_list[i], output_gap_list[i]))
            except IndexError:
                break

    if meeting_date not in date_to_taylor_1999:
        date_to_taylor_1999[meeting_date] = []
        for i in range(max_length):
            try:
                if pd.isna(CPI_list[i]):
                    CPI_list[i] = ''
                if pd.isna(output_gap_list[i]):
                    output_gap_list[i] = ''
                date_to_taylor_1999[meeting_date].append(taylor_1999_equation(CPI_list[i], output_gap_list[i]))
            except IndexError:
                break

date_to_inertial_taylor_1999 = {}
for meeting_date in meeting_date_list:
    CPI_list = GB_date_to_CPI[meeting_date]
    meeting_date = datetime.strftime(meeting_date, '%m/%d/%Y')
    output_gap_list = [x for x in output_gap_df[meeting_date].tolist() if isinstance(x, float)]
    max_length = max(len(CPI_list), len(output_gap_list))

    if meeting_date not in date_to_inertial_taylor_1999:
        date_to_inertial_taylor_1999[meeting_date] = []
        for i in range(max_length):
            try:
                if i == 0:
                    date_to_inertial_taylor_1999[meeting_date].append('')
                    continue
                if pd.isna(CPI_list[i]):
                    CPI_list[i] = ''
                if pd.isna(output_gap_list[i]):
                    output_gap_list[i] = ''
                date_to_inertial_taylor_1999[meeting_date].append(inertial_taylor_1999_equation(CPI_list[i], output_gap_list[i], date_to_taylor_1999[meeting_date][i - 1]))
            except IndexError:
                break

def write_to_google_sheets(dictionary, worksheet):

    date_list = ['DATE']
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
write_to_google_sheets(date_to_inertial_taylor_1999, 'inertial_taylor_1999_projections')

def quarter_ahead_expectations(dictionary, quarter_ahead):
    quarter_ahead_expectations_list = []
    for date, predicted_ffr in dictionary.items():
        quarter_ahead_expectations_list.append(predicted_ffr[quarter_ahead])
    return quarter_ahead_expectations_list

plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["figure.autolayout"] = True
plt.gcf().canvas.manager.set_window_title('FOMC Equations')
plt.plot(meeting_date_list, quarter_ahead_expectations(date_to_taylor_1993, 1), color = 'red', linewidth = 2, label = 'Taylor 1993 Rule')
plt.plot(meeting_date_list, quarter_ahead_expectations(date_to_taylor_1999, 1), color = 'blue', linewidth = 2, label = 'Taylor 1999 Rule')
plt.plot(meeting_date_list, quarter_ahead_expectations(date_to_inertial_taylor_1999, 1), color = 'green', linewidth = 2, label = 'Inertial Taylor 1999 Rule')
# TODO: how many quarters ahead?
plt.title('Comparison of Projected FFR by FOMC Equations', fontweight = 'bold', backgroundcolor = 'silver')
plt.xlabel('MEETING DATE')
plt.ylabel('ESTIMATED FFR')
plt.xticks(meeting_date_list[::8], rotation = 45)
plt.legend(loc = 'upper right')
plt.grid()

plt.show()