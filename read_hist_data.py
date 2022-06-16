from attr import has
from numpy import var
import pandas as pd
import xml.etree.ElementTree as et

read_file = pd.read_csv ('HISTDATA.TXT')
read_file.to_csv ('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/histdata.csv', index=None)
df = pd.read_csv('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/histdata.csv')

root: et.Element = et.parse('pyfrbus_package/models/model.xml').getroot()

all_variable: et.ElementTree = root.findall("variable")

name_list = []
equation_type_list = []
sector_list = []
definition_list = []
has_expected_list = []
for variable in all_variable:
    name = variable.find('name').text
    equation_type = ''
    sector = ''
    definition = ''
    description = ''
    has_expected = 'false'
    if variable.find('equation_type') is not None:
        equation_type = variable.find('equation_type').text
    if variable.find('sector') is not None:
        sector = variable.find('equation_type').text
    if variable.find('definition') is not None:
        definition = variable.find('definition').text
        if '(VAR exp.)' in definition:
            has_expected = 'true'

    name_list.append(name)
    equation_type_list.append(equation_type)
    sector_list.append(sector)
    definition_list.append(definition)
    has_expected_list.append(has_expected)