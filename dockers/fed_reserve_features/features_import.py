from full_fred.fred import Fred
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
from pandas import json_normalize
import pytrends
from pytrends.request import TrendReq
from kafka import KafkaConsumer, TopicPartition
import logging
import sys

# This script downloads data from Federal Reserve, Google Trends, Bitcoin Fear Index
# and data from TradingView via Kafka topic

def fed_features(main_df, single=False):

    fred = Fred()

    files = {
        "Total_Assets_(Change_in_Wednesday_Level_from_Year_Ago_Level)": "RESPPMAXCH52NWW",  # weekly
        "US_Treasury_General_Account": 'WTREGEN',  # weekly  √
        "BB_US_Emerging_Markets_Liquid": "BAMLEM3RBBLCRPIUSSYTW",  # daily √
        "Nominal_Broad_US_Dollar_Index": "DTWEXBGS",  # 1-2 days √
        "CBOE_Volatility_Index_VIX": "VIXCLS", # VIX √
        "CBOE_Gold_ETF_Volatility_Index": "GVZCLS", # Gold VIX √
        "US_Treasury_General_Account_(Change_in_Wednesday_Level_from_Year_Ago_Level)": 'RESPPLLDTXAWXCH52NWW',  # weekly
        "US_30_Year_Fixed_Rate_Mortgage_Average": "MORTGAGE30US",  # weekly √
        "Commercial_Paper_Outstanding": "COMPOUT",  # weekly √
        "Equity_Market-related_Economic_Uncertainty_Index": "WLEMUINDXD",  # daily
        "OECD_Indicator_US": "BSCICP03USM665S",  # monthly √
        "10-Year_Breakeven_Inflation_Rate": "T10YIE",  # daily √
        "Chicago_Fed_National_Financial_Conditions_Index": "NFCI",  # weekly, delayed √
        "M2": "WM2NS",  # monthly √
        "Producer_Price_Index_by_Commodity": "PPIACO",  # monthly √
    }

    for asset, symbol in files.items():
        if single:
            df = fred.get_series_df(symbol, sort_order='desc', limit=1)
            df['date'] = yesterday
        else:
            df = fred.get_series_df(symbol)
        df[symbol] = df['value'].replace(to_replace='.', method='ffill')
        main_df = main_df.copy().merge(df[[symbol, 'date']], on='date', how='left')
        main_df[symbol] = main_df[symbol].replace(to_replace=None, method='ffill')

    main_df['date'] = pd.to_datetime(main_df['date'], format='%Y-%m-%d')
    print("Fed features successfully downloaded")

    return main_df


def fear_index(single=False):

    limit = 2 if single else 0
    response = requests.get(f'https://api.alternative.me/fng/?limit={limit}&format=json&date_format=world')
    response_json = response.json()
    df = json_normalize(response_json, 'data')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d-%m-%Y')
    df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
    df = df.rename(columns={'timestamp': 'date', 'value': 'fear_index'})

    df = df[['date', 'fear_index']]
    df = df.head(1) if single else df
    print("Fear Index successfully downloaded")

    return df


def google_trends(single=False):

    pytrends = TrendReq(hl='en-US', tz=0, retries=10)
    pytrends.build_payload(['bitcoin'], timeframe='today 5-y', gprop='')
    trends = pytrends.interest_over_time()['bitcoin']
    df = pd.DataFrame(trends).tail(1) if single else pd.DataFrame(trends)
    df['date'] = yesterday if single else df.index
    df = df.rename(columns={'bitcoin': 'bitcoin_google_trend'})
    df = df.reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    print("Google trends successfully downloaded")

    return df


def tradingview_data(topic):
    print("Start consuming Kafka message for", topic, "topic")
    #logging.basicConfig(level=logging.INFO)

    consumer = KafkaConsumer(topic,
                            bootstrap_servers=['kafka-service:9092'],
                            group_id=None,
                            #api_version=(0, 10, 1),
                            auto_offset_reset='earliest',
                            enable_auto_commit=False,
                            )

    consumer.subscribe(topic)
    partition = TopicPartition(topic, 0)
    end_offset = consumer.end_offsets([partition])
    consumer.seek(partition, list(end_offset.values())[0] - 1)


    for msg in consumer:
        if msg is None or msg == '':
            logging.error("No messages received from Kafka!")
        else:
            #logging.info(" current message is = {}".format(json.loads(msg.value)))
            json_output = json.loads(msg.value)
            break

    df = pd.json_normalize(json_output, 'table')
    df['date'] = pd.to_datetime(df['$time'], unit='s')
    df = df[['date', topic]]
    return df


if __name__ == '__main__':

    yesterday = datetime.now() - timedelta(1)
    yesterday = datetime.strftime(yesterday, '%Y-%m-%d')

    # if single = True: idx = pd.date_range(yesterday, yesterday)
    single = True if int(sys.argv[1]) == 1 else False

    start_from = yesterday if single else '2010-01-01'
    idx = pd.date_range(start_from, yesterday)
    main_df = pd.DataFrame()
    main_df = main_df.assign(date=idx.strftime('%Y-%m-%d').tolist())

    main_df = fed_features(main_df, single=single)
    fi_df = fear_index(single=single)
    gt_df = google_trends(single=single)

    dataframes = {
        'fear_index': fi_df,
        'bitcoin_google_trend': gt_df
    }

    for symbol, df in dataframes.items():
        print('Merging', symbol, 'dataframe')
        main_df = main_df.copy().merge(df, on='date', how='left')
        main_df[symbol] = main_df[symbol].replace(to_replace=None, method='ffill')

    topics = ['bitcoin_dominance', 'bitcoin_market_cap']

    for topic in topics:
        df = tradingview_data(topic)
        main_df = main_df.copy().merge(df, on='date', how='left')

    main_df.to_csv('output.csv', index=False)

