import pandas as pd 

translator = pd.read_csv('countries_codes_and_coordinates.csv')
translator['Alpha-2 code'] = translator['Alpha-2 code'].str.replace(' ', '').str.replace('"', '')
translator['Alpha-3 code'] = translator['Alpha-3 code'].str.replace(' ', '').str.replace('"', '')
dicionario = {}
for row, value in translator.iterrows():
    dicionario[value['Alpha-2 code']] = value['Alpha-3 code']



