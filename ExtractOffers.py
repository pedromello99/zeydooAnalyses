import requests
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from curl_cffi import requests as curl_cffi

# Get the data from the API

translator = pd.read_csv('countries_codes_and_coordinates.csv')
translator['Alpha-2 code'] = translator['Alpha-2 code'].str.replace(' ', '').str.replace('"', '')
translator['Alpha-3 code'] = translator['Alpha-3 code'].str.replace(' ', '').str.replace('"', '')
dicionario = {}

for row, value in translator.iterrows():
    dicionario[value['Alpha-2 code']] = value['Alpha-3 code']

def TwoToTree(twocode):
    try:
        return dicionario[twocode]
    except:
        print(twocode)
        return twocode

def MakeLogin(login, password):
    fingerprint = curl_cffi.get("https://tls.browserleaks.com/json", impersonate="chrome101")
    fingerprint = fingerprint.json()['ja3_hash']
    json_data = {
    'username': login,
    'password': password,
    'type': 'publisher',
    'partner_alias': 'offerpartner',
    'fingerprint': fingerprint,
    'captcha': '',
    }

    response = requests.post('https://app.zeydoo.com/api/client/public/login/', json=json_data)
    return response.json()['api_token']

def GetOffers(token):
    tudo = []
    page = 1
    total_pages = 2
    ignore = ['A1', 'A2', 'EU', 'AP']
    with requests.Session() as s:
        while page <= total_pages:
            params = {
                'order_by': 'id',
                'dest': 'DESC',
                'page_size': '50',
                'page': str(page),
                'is_data_offers': '0',
            }
            s.headers.update({'authorization': 'Bearer {}'.format(token)})

            response = s.get('https://app.zeydoo.com/api/client/offers_pagination/', params=params)
            page = response.json()['page']
            total_pages = response.json()['total_pages']
            for item in response.json()['items']:
                for cota in item['rates']:
                    valor = cota['amount']
                    for pais in cota['countries']:
                        if pais.upper() in ignore:
                            continue
                        tudo.append({'id': item['id'], 'Nome': item['title'], 'Payout': valor, 'País - 3': TwoToTree(pais.upper()),
                                        'País - 2': pais.upper(), 'País - Nome': translator[translator['Alpha-2 code'] == pais.upper()]['Country'].values[0],
                                        'status': item['status'], 'vertical': item['vertical']['name'], 'type': item['type'], 
                                        'conversion_type': item['conversion_type']['name'], 'top': item['tag']['is_top'], 'is_exclusive': item['tag']['is_exclusive'],
                                        'is_excluded': item['is_excluded'], 'redirectless_type': item['redirectless_type'], 'type': item['type']})
            page += 1
    df = pd.DataFrame(tudo)
    df.to_csv('offers.csv', index=False)
    return df

def inserttoDB(df, engine):
    engine = create_engine(engine)
    df.to_sql('zeydoo', engine, if_exists='replace', index=False)
    print('Done')

if __name__ == '__main__':
    load_dotenv()
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    engine = os.getenv('ENGINE')
    token = MakeLogin(login, password)
    df = GetOffers(token)
    # df = pd.read_csv('offers.csv')
    df['País - 3'] = df['País - 3'].str.replace(' ', '').str.replace('"', '')
    df['País - 2'] = df['País - 2'].str.replace(' ', '').str.replace('"', '')
    df['País - Nome'] = df['País - Nome'].str.replace(' ', '')
    df['País - Nome'] = df['País - Nome'].str.replace('"', '')
    df.to_csv('offers.csv', index=False)
    inserttoDB(df, engine)
