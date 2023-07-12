from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Timer

import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
import pytz
import sys
import ast


class TestApp(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)

        self.data = []
        self.strikes = ast.literal_eval(sys.argv[1])[:-1]
        self.symbol = 'SPY'
        self.option = sys.argv[2]
        self.day = str(ast.literal_eval(sys.argv[1])[-1])


    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def contractDetails(self, reqId, contractDetails):
        print("contractDetails: ", reqId, " ", contractDetails)
        return contractDetails

    def historicalData(self, reqId, bar):
        strike = self.strikes[reqId]
        contract = self.symbol + '-' + self.day + '-' + str(strike) + '-' + self.option

        #print(f'Time: {bar.date} Open: {bar.open} High: {bar.high} Low: {bar.low} Close: {bar.close}'
        #      f'Contract: {contract}')

        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, contract])

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)


def main():

    app = TestApp()
    app.connect('ib-gateway-service', 4002, 0)

    app.nextorderId = 0
    id = 0

    for strike in app.strikes:

        contract = Contract()
        contract.symbol = app.symbol
        contract.secType = 'OPT'
        contract.exchange = 'SMART'
        contract.lastTradeDateOrContractMonth = app.day
        contract.right = app.option
        contract.multiplier = '100'
        contract.currency = 'USD'
        contract.strike = strike

        app.reqHistoricalData(id, contract, '', '13 D', '5 mins', 'BID_ASK', 0, 2, False, [])
        app.nextorderId += 1
        id += 1

    Timer(100, app.disconnect).start()
    app.run()
    return app.data


if __name__ == '__main__':

    data = main()
    df = pd.DataFrame(data, columns=['DateTime', 'Open', 'High', 'Low', 'Close', 'Contract'])
    df['DateTime'] = pd.to_datetime(df['DateTime'], unit='s')
    df.to_csv(f'SPY-{ast.literal_eval(sys.argv[1])[-1]}-{sys.argv[2]}.csv', index=False)
