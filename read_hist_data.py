import pandas as pd

read_file = pd.read_csv ('HISTDATA.TXT')
read_file.to_csv ('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/histdata.csv', index=None)
df = pd.read_csv('/Users/franksi-unchiu/Desktop/cs200python/RAsummer2022/histdata.csv')