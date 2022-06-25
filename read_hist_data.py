import pandas as pd
import xml.etree.ElementTree as et
import pygsheets
from pygsheets.datarange import DataRange

read_file = pd.read_csv ('HISTDATA.TXT')
read_file.to_csv('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/histdata.csv', index = None)
df = pd.read_csv('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/histdata.csv')
root: et.Element = et.parse('pyfrbus_package/models/model.xml').getroot()
all_variable: et.ElementTree = root.findall("variable")
sheet = pygsheets.authorize(service_account_file = 'write_into_google_sheet.json').open('Summer RA')

name_list = ['Name']
equation_type_list = ['Equation Type']
sector_list = ['Sector']
definition_list = ['Definition']
has_expectations_data_list = ['Has Expectations Data']

for variable in all_variable:
    name = variable.find('name').text
    equation_type = ''
    sector = ''
    definition = ''
    has_expectations_data = 'false'

    if variable.find('equation_type') is not None:
        equation_type = variable.find('equation_type').text
    if variable.find('sector') is not None:
        sector = variable.find('equation_type').text
    if variable.find('definition') is not None:
        definition = variable.find('definition').text
        if '(VAR exp.)' in definition:
            has_expectations_data = 'true'

    name_list.append(name)
    equation_type_list.append(equation_type)
    sector_list.append(sector)
    definition_list.append(definition)
    has_expectations_data_list.append(has_expectations_data)

try:
    hist_data_sheet = sheet.add_worksheet('hist_data', rows = 368, cols = 5)
    hist_data_sheet.update_col(1, name_list)
    hist_data_sheet.update_col(2, equation_type_list)
    hist_data_sheet.update_col(3, sector_list)
    hist_data_sheet.update_col(4, definition_list)
    hist_data_sheet.update_col(5, has_expectations_data_list)
    bold = hist_data_sheet.cell('A1')
    bold.set_text_format('bold', True)
    DataRange('A1','E1', worksheet = hist_data_sheet).apply_format(bold)
except:
    pass