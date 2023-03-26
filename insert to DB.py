import pandas as pd
from sqlalchemy import create_engine


df = pd.read_csv('offers.csv', sep=',')


print(df)

engine = create_engine('mysql://guepardo_fretebras:xixtMzxEEKNJKSGZ@140.238.191.48:3306/guepardo_fretebras')
df.to_sql('zeydoo', engine, if_exists='replace', index=False)