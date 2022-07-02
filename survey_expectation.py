import pandas as pd
import matplotlib.pyplot as plt

class Survey:

    def __init__(self, SCE_relative_file_path, SCE_spreadsheet, SCE_column, statistic, y_label):

        SCE_excel = pd.ExcelFile(SCE_relative_file_path)
        SCE_df = pd.read_excel(SCE_excel, SCE_spreadsheet, skiprows=[0, 1, 2])
        SCE_year_month_list = SCE_df.iloc[:, [0]].values.tolist()
        statistic_list = SCE_df.loc[:, SCE_column].tolist()

        for i in range(len(SCE_year_month_list)):
            SCE_year_month_list[i] = str(SCE_year_month_list[i][0])[:4] + '-' + str(SCE_year_month_list[i][0])[4:]

        UMSC_df = pd.read_excel('survey_data/sca-tableall-on-2022-Jul-02.xls', usecols = ['Month', 'yyyy', 'px1_med_all'], skiprows = [0])
        UMNSC_year_list = UMSC_df.yyyy.unique()
        UMSC_month_list = UMSC_df.Month.unique()
        UMSC_year_to_month_to_statistic = {}

        for year in UMNSC_year_list:
            if year not in UMSC_year_to_month_to_statistic:
                UMSC_year_to_month_to_statistic[year] = {}
            for month in UMSC_month_list:
                if month not in UMSC_year_to_month_to_statistic[year]:
                    UMSC_year_to_month_to_statistic[year][month] = UMSC_df.loc[UMSC_df['yyyy'].eq(year) & UMSC_df['Month'].eq(month)].values

        # numpy

        print(UMSC_year_to_month_to_statistic)

        plt.rcParams["figure.figsize"] = [12, 6]
        plt.rcParams["figure.autolayout"] = True
        plt.gcf().canvas.manager.set_window_title('Survey')
        plt.plot(SCE_year_month_list, statistic_list, color = 'red', linewidth = 2, label = 'Survey of Consumer Expectations')
        plt.title(statistic + ' Survey Data', fontweight = 'bold', backgroundcolor = 'silver')
        plt.xlabel('YEAR_MONTH', labelpad = 10)
        plt.ylabel(y_label, labelpad = 10)
        plt.xticks(SCE_year_month_list[::4], rotation = 45)
        plt.legend(loc = 'upper right')
        plt.grid()

        plt.show()

# inflation
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Inflation expectations', 'Median one-year ahead expected inflation rate', 'Inflation', 'EXPECTED INFLATION RATE')
# RGDP
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Earnings growth', 'Median expected earnings growth', 'RGDP', 'EXPECTED RGDP GROWTH RATE')
# unemployment
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Unemployment Expectations', 'Mean probability that the U.S. unemployment rate will be higher one year from now', 'Unemployment Rate', 'PROBABILITY US UNEMPLOYMENT RATE WILL BE HIGHER NEXT YEAR')
# interest rate
Survey('survey_data/FRBNY-SCE-Data.xlsx', 'Interest rate expectations', 'Mean probability of higher average interest rate on savings accounts one year from now', 'Interest Rate', 'PROBABILITY OF HIGHER INTEREST RATE NEXT YEAR')

# https://data.sca.isr.umich.edu/subset/codebook.php
# INEX_MED, UMEX_R, RATEX_R, PX1_MED