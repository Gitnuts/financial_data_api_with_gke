from binance.client import Client
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import argparse
import os


parser = argparse.ArgumentParser(description='Retrieves a feature matrix for a cryptocurrency pair.'
                                             'Specify number of days -d')

parser.add_argument("-s", "--single", help="Whether to download a single day data or full data set")
parser.add_argument("-p", "--pair", help="Cryptocurrency pair. Default is BTCUSDT")
args = parser.parse_args()


if __name__ == '__main__':

    BINANCE_READ_API_KEY = os.environ.get('BINANCE_API_KEY')
    BINANCE_READ_SECRET_KEY = os.environ.get('BINANCE_SECRET_KEY')

    yesterday = datetime.now() - timedelta(1)
    yesterday = datetime.strftime(yesterday, '%d %b, %Y')

    today = datetime.now()
    today = datetime.strftime(today, '%d %b, %Y')

    start_from = '01 Jan 2018' if args.single is None else yesterday

    client = Client(BINANCE_READ_API_KEY, BINANCE_READ_SECRET_KEY)
    symbol = 'BTCUSDT' if args.pair is None else args.pair
    klines = client.get_historical_klines(symbol,
                                          Client.KLINE_INTERVAL_5MINUTE,
                                          start_from,
                                          today
                                          )

    df = pd.DataFrame(np.array(klines),
                      columns=['TIMESTAMP_OPEN', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME',
                               'TIMESTAMP_CLOSE', 'QUOTE_VOLUME', 'TRADES',
                               'TAKER_BUY_BASE', 'TAKER_BUY_QUOTE', 'IGNORE'])

    df = df[:].astype(np.float64)
    df['timestamp'] = pd.to_datetime(pd.to_numeric(df['TIMESTAMP_OPEN'], downcast="integer") * 1E6)
    df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.strftime('%Y-%m-%d')
    df = df.drop(columns=['IGNORE', 'TIMESTAMP_OPEN', 'TIMESTAMP_CLOSE'])

    # set the main dataframe to capture NULL rows
    idx = pd.date_range(start_from, today, freq='5min')
    main_df = pd.DataFrame()
    main_df = main_df.assign(timestamp=idx.strftime('%Y-%m-%d %H:%M:%S').tolist())
    main_df['timestamp'] = pd.to_datetime(main_df['timestamp'], format='%Y-%m-%d %H:%M:%S')
    main_df = main_df.copy().merge(df, on='timestamp', how='left')

    # drop the last row as it contains today's data
    main_df = main_df[:-1]
    print('Uploading to GCS...')
    main_df.to_csv('output.csv', index=False)
