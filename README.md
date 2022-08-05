# RAsummer2022

This repository contains all of the code I wrote as a Research Assistant over Summer of 2022. I assisted Amy Handlan, economics professor at Brown University, in studying how Federal Reserve communication strategies influence consumer and industry expectations, monetary policy, survey projections, construction of economic rules, etc.

Libraries/technologies used: requests, Beautiful Soup, regex, datetime, pathlib, pandas, pygsheets, matplotlib, ElementTree XML API, etc.

The other_code folder contains miscellaneous code.

The other_data folder contains a variety of data used throughout the project.

The pyfrbus_package folder contains the FRB/US model, a model of the US economy developed by the Federal Reserve Board for forecast, analysis, and research.

The spf_plot_data folder contains all the data of the economic variables of interest from the Survey of Professional Forecasters. Specifically, the variables are RGDP, PRGDP, CPI, CORECPI, PCE, COREPCE, RR1_TBILL_PGDP, and SPR_TBOND_TBILL.

The survey_data folder contains all the data of the economic variables of interest from various surveys of economic projections. Specifically, the surveys are the Survey of Consumer Expectations (SCE) from the NY Federal Reserve, University of Michigan Survey of Consumers, Survey of Professional Forecasters with the Philadelphia Federal Reserve, Livingston Survey with the Philadelphia Federal Reserve, and Summary of Economic Projections/Tealbook and Greenbook Dataset.

automated_saver.py scraps the Federal Open Market Committee website for Federal Open Market Committee Press Statements for meetings from 2017 to 2022 (could include more). It automates the processing of saving the statements as text files into folders organized by years.

output_gap.py parses CPI and output gap data to generate the projected federal funds rate by the Taylor 1993 Rule, Taylor 1999 Rule, and Inertial Taylor Rule 9 quarters ahead of each Federal Open Market Committee meeting. It writes that data into Google Sheets and plots it.

read_hist_data.py reads a text file of projected values of hundreds of different economic variables and compares them to the variable descriptions in an XML file in the pyfrbus model. It extracts necessary information about each variable (name, type, sector, definition, expectations) and writes it into Google Sheets.

spf_plot.py parses data and plots the 25th, median, and 75th percentile and IQR of the variables forecasted by the Survey of Professional Forecasters as described in the spf_plot_data folder, including the calculated growth of these variables.

survey_expectations.py parses data and plots the projected inflation, RGDP, unemployment, and interest rate from surveys described in the survey_data folder.

timeline.py parses data on the evolution of Federal Open Market Committee policy rules and equations over time and plots them on a timeline.

webscrapper.py utilizes BeautifulSoup to scrap the Federal Open Market Committee website for Federal Open Market Committee Press Statements for meetings from 1999 to 2022 (could include more) to extract necessary information about each meeting. It collects information on Statement Release Time, Press Conference Start Time, SEP Released, Minutes Release Date, and Internal Material Released. It utilizes nltk and spacy to extract information about voting patterns of Federal Open Market Committee officials by parsing the statements to obtain the Number of Members Voting in Favor, Number of Members Not in Favor, Names in Favor, Names Not in Favor, and Reason for Dissent. It writes all of this information into Google Sheets.