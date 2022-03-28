import os
import sys
import yaml
import requests
import pandas as pd
import datetime

from sdk import Sedmax, ElectricalArchive


def get_data(config, mode='onestep'):

    if mode not in ['onestep', 'multistep']:
        raise Exception('Wrong mode specified')

    SEDMAX_config = config['vars']
    days_to_load = config['resources']['days_to_load']

    s = Sedmax(SEDMAX_config['SEDMAX_URL'])
    s.login(SEDMAX_config['SEDMAX_USERNAME'], SEDMAX_config['SEDMAX_PASSWORD'])
    el = ElectricalArchive(s)

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    days_ago = (now - datetime.timedelta(days_to_load)).strftime('%Y-%m-%d')
    year = now.strftime('%Y')

    df = el.get_data([SEDMAX_config['dev-101']], ['30min'], days_ago, date).reset_index()
    df = df.rename(columns={SEDMAX_config['dev-101']:'value'})

    #
    r = requests.get(f'https://isdayoff.ru/api/getdata?year={year}')
    days_off = [x for x in r.text]
    days_off = dict(enumerate(days_off))

    df['dayofweek'] = df['dt'].dt.dayofweek.astype(str)
    df['dayoff'] = df['dt'].dt.day_of_year.map(days_off)
    df['hour'] = df['dt'].dt.hour.astype(str)

    if mode == 'onestep':
        df[['mean', 'median', 'max', 'min']] = df.rolling(window=6, min_periods=0)['value'].agg(
            ['mean', 'median', 'max', 'min']).fillna(0)
        for i in range(1, 13):
            df[f'value_{i}'] = df['value'].shift(i).diff()

    else:
        for i in range(1, 336, 2):
            df[f'value_{i}'] = df['value'].shift(i).diff()

        for i in range(1, 49):
            df[f'target_{i}'] = df['value'].shift(-i)

    df = pd.get_dummies(df)

    return df
