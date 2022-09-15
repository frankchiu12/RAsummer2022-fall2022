import json
import requests
import pandas as pd

response = requests.get('https://ntrs.nasa.gov/api/citations/search?published.lte=1975')
f = open('NASA_output/NASA_json_result.json', 'w')
f.write(response.text)
f.close()

data = json.load(open('NASA_output/NASA_json_result.json'))
df = pd.DataFrame(data['results'])
df.to_csv('NASA_output/NASA_output_b4_1975.csv', index = False)