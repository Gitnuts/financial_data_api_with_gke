from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import SetOfString, SetOfFloat
from threading import Timer


from datetime import timedelta, datetime
import yfinance as yf
import pandas as pd
import sys


class TestApp(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)

        self.expirations_data = {}
        self.strikes_data = {}

    def error(self, reqId, errorCode, errorString):
        #print(reqId," ", errorCode," ", errorString)
        return None


    def nextValidId(self, orderId):
        self.start()

    def securityDefinitionOptionParameter(self, reqId: int, exchange: str,
        underlyingConId: int, tradingClass: str, multiplier: str,
        expirations: SetOfString, strikes: SetOfFloat):

        super().securityDefinitionOptionParameter(reqId, exchange, underlyingConId, tradingClass,
                                                  multiplier, expirations, strikes)

        if exchange == 'SMART':
            self.strikes_data = strikes
            self.expirations_data = expirations

    def securityDefinitionOptionParameterEnd(self, reqId):
        return None

    def start(self):
        self.reqSecDefOptParams(1, "SPY", "", "STK", 756733)

    def stop(self):
        self.done = True
        self.disconnect()


def ib_main():

    app = TestApp()
    app.nextOrderId = 0
    app.connect('ib-gateway-service', 4002, 0)

    Timer(20, app.stop).start()

    app.run()

    return app.expirations_data, app.strikes_data


def filter_days(expirations):
    for expiration in expirations:
        expiration = datetime.strptime(expiration, '%Y%m%d')
    return min(expirations)


def filter_strikes(strikes, diff, stock):
    start = datetime.today() - timedelta(30)
    start = start.strftime('%Y-%m-%d')

    end = datetime.today() - timedelta(30 - diff)
    end = end.strftime('%Y-%m-%d')

    yahoo_data = yf.download(stock, start=start, end=end, interval="1d", progress=False)
    yahoo_data.index = pd.to_datetime(yahoo_data.index, utc=True)

    local_max = yahoo_data.loc[yahoo_data['High'].idxmax()]['High']
    local_min = yahoo_data.loc[yahoo_data['Low'].idxmin()]['Low']

    for strike in strikes.copy():
        if strike <= local_min or strike >= local_max:
            strikes.remove(strike)

    return strikes


if __name__ == '__main__':

    expirations_data, strikes_data = ib_main()
    strikes = filter_strikes(strikes_data, 13, 'SPY')
    strikes = list(strikes)
    confirmed_strikes = []

    for strike in strikes:
        if strike % 2 == 0:
            confirmed_strikes.append(strike)

    strike_days = []
    days = []

    for x in range(17, 30):
        strike_days.append((datetime.now()+timedelta(days=x)).strftime('%Y%m%d'))
    for strike_day in expirations_data:
        if strike_day in strike_days:
            days.append(int(strike_day))

    #last_day = filter_days(expirations_data)
    confirmed_strikes.append(min(days))

    print(confirmed_strikes)
