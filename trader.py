from binance.client import Client
import talib as ta
import numpy as np
import SuperTrend as super
from datetime import datetime
import time
import requests
import Tillson as till
import sqlite3 as conn

class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """
    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret, {"timeout": 100})


if __name__ == '__main__':
    filename = 'credential.txt'
    connection = BinanceConnection(filename)
    interval = '5m'
    Db = conn.connect("tradeDatabase.db")

    while True:
        time.sleep(10)
        try:
            sy = connection.client.get_all_tickers()
            for sym in sy:
                symbol = sym["symbol"]
                price = sym["price"]
                #print("symbol", symbol)

                klines = connection.client.get_klines(symbol=symbol, interval=interval)
                open_time = [int(entry[0]) for entry in klines]
                open = [float(entry[1]) for entry in klines]
                high = [float(entry[2]) for entry in klines]
                low = [float(entry[3]) for entry in klines]
                close = [float(entry[4]) for entry in klines]
                last_closing_price = close[-1]
                previous_closing_price = close[-2]
                #print('anlık kapanış fiyatı', last_closing_price, ', bir önceki kapanış fiyatı', previous_closing_price)
                close_array = np.asarray(close)

                high_array = np.asarray(high)
                low_array = np.asarray(low)
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                new_time_x = [date.strftime("%y-%m-%d") for date in new_time]

                #print("date", datetime.now())

                close_finished = close_array[:-1]
                macd, macdsignal, macdhist = ta.MACD(close_finished, fastperiod=12, slowperiod=26, signalperiod=9)
                rsi = ta.RSI(close_finished, timeperiod=14)
                supertrend = super.generateSupertrend(close_array, high_array, low_array, atr_period=10,
                                                      atr_multiplier=2)

                volume_factor = 0.7
                t3length = 8
                tillson = till.generateTillsonT3(close_array, high_array, low_array, volume_factor=volume_factor,
                                              t3Length=t3length)


                t3_last = tillson[-1]
                t3_previous = tillson[-2]
                t3_prev_previous = tillson[-3]

                cs = Db.cursor()

                # kırmızıdan yeşile dönüyor
                if t3_last > t3_previous and t3_previous < t3_prev_previous:
                    cs.execute(
                        """select * from Trader where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 'TILLSON'""" % (
                            symbol))
                    dataSet = cs.fetchone()
                    if dataSet is None:
                        cs.execute("insert into Trader values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   ("BUY", "TILLSON", symbol, "ACTIVE", 100, price, 100 / float(price), datetime.now(),
                                    None, None, None,
                                    None))
                    Db.commit()

                    #print('tillson t3 buy signal, from red to green ' ,symbol, " price:", price)
                    #cs.execute("insert into SignalLogs values (?, ?, ?, ?, ?)",("BUY","TILLSON",symbol,price,datetime.now()))

                # yeşilden kırmızıya dönüyor
                elif t3_last < t3_previous and t3_previous > t3_prev_previous:
                    cs.execute(
                        """select * from Trader where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 'TILLSON'""" % (
                            symbol))
                    dataSet = cs.fetchone()
                    if dataSet is not None:
                        quant = float(dataSet[6])
                        ex = float(dataSet[4])
                        print("quant", quant)
                        print("price", price)
                        closed_total = quant * float(price)
                        print("closed_total", closed_total)
                        prof = closed_total - ex
                        cs.execute(""" Update Trader set TransactionStatus = 'COMPLETED', sold_price = '%s', sold_time = '%s', 
                        closed_total = '%s', profit = '%s', isactive = 'INACTIVE' where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 
                        'TILLSON'""" % (price, datetime.now(), closed_total, prof, symbol))
                        Db.commit()


                son_kapanis = close_array[-1]
                onceki_kapanis = close_array[-2]

                son_supertrend_deger = supertrend[-1]
                onceki_supertrend_deger = supertrend[-2]

                # renk yeşile dönüyor, trend yükselişe geçti
                if son_kapanis > son_supertrend_deger and onceki_kapanis < onceki_supertrend_deger:
                    #print('al supertrend', symbol, " price:", price)
                    #cs.execute("insert into SignalLogs values (?, ?, ?, ?, ?)",("BUY", "SUPERTREND", symbol, price, datetime.now()))
                    cs.execute(
                        """select * from Trader where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 'SUPERTREND'""" % (
                            symbol))
                    dataSet = cs.fetchone()
                    if dataSet is None:
                        cs.execute("insert into Trader values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   ("BUY", "SUPERTREND", symbol, "ACTIVE", 100, price, 100 / float(price), datetime.now(),
                                    None, None, None,
                                    None))
                    Db.commit()

                # renk kırmızıya dönüyor, trend düşüşe geçti
                if son_kapanis < son_supertrend_deger and onceki_kapanis > onceki_supertrend_deger:
                    cs.execute(
                        """select * from Trader where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 'SUPERTREND'""" % (
                            symbol))
                    dataSet = cs.fetchone()
                    if dataSet is not None:
                        quant = float(dataSet[6])
                        ex = float(dataSet[4])
                        print("quant", quant)
                        print("price", price)
                        closed_total = quant * float(price)
                        print("closed_total", closed_total)
                        prof = closed_total - ex
                        cs.execute(""" Update Trader set TransactionStatus = 'COMPLETED', sold_price = '%s', sold_time = '%s', 
                                            closed_total = '%s', profit = '%s', isactive = 'INACTIVE' where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 
                                            'SUPERTREND'""" % (price, datetime.now(), closed_total, prof, symbol))
                        Db.commit()
                    #print('sat supertrend', symbol, " price:", price)
                    # cs.execute("insert into SignalLogs values (?, ?, ?, ?, ?)",
                    #            ("SELL", "SUPERTREND", symbol, price, datetime.now()))
                    # Db.commit()

                if len(macd) > 0:
                    # print("len(macd) > 0")
                    last_macd = macd[-1]
                    last_macd_signal = macdsignal[-1]

                    previous_macd = macd[-2]
                    previous_macd_signal = macdsignal[-2]

                    rsi_last = rsi[-1]

                    macd_cross_up = last_macd > last_macd_signal and previous_macd < previous_macd_signal

                    if macd_cross_up and rsi_last > 50:
                        #print('al mac + rsi', symbol, " price:", price)
                        cs.execute("insert into SignalLogs values (?, ?, ?, ?, ?)",
                                   ("BUY", "MACD + RSI", symbol, price, datetime.now()))
                        Db.commit()


        except requests.exceptions.ReadTimeout:
            print("timeout")
            pass





                            # buy_order = connection.client.order_market_buy(
                            #     symbol=symbol,
                            #     quantity=0.1)





        # try:
        #
        #        # klines = connection.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        #
        # except Exception as exp:
        #     print(exp.status_code, flush=True)
        #     print(exp.message, flush=True)



        # open = [float(entry[1]) for entry in klines]
        # high = [float(entry[2]) for entry in klines]
        # low = [float(entry[3]) for entry in klines]
        # close = [float(entry[4]) for entry in klines]
       # print(sy)
#
#         last_closing_price = close[-1]
#
#         previous_closing_price = close[-2]
#
#         print('anlık kapanış fiyatı', last_closing_price, ', bir önceki kapanış fiyatı', previous_closing_price)
#
#         close_array = np.asarray(close)
#         close_finished = close_array[:-1]
#
#         macd, macdsignal, macdhist = ta.MACD(close_finished, fastperiod=12, slowperiod=26, signalperiod=9)
#         rsi = ta.RSI(close_finished, timeperiod=14)
# #        print('macd', macd)
#  #       print('macdsignal', macdsignal)
#   #      print('macdhist', macdhist)
#
#
#         if len(macd) > 0:
#             print("len(macd) > 0")
#             last_macd = macd[-1]
#             last_macd_signal = macdsignal[-1]
#
#             previous_macd = macd[-2]
#             previous_macd_signal = macdsignal[-2]
#
#             rsi_last = rsi[-1]
#
#             macd_cross_up = last_macd > last_macd_signal and previous_macd < previous_macd_signal
#
#             if macd_cross_up and rsi_last > 50:
#                 print('al sinyali', flush=True)
#
#                 # mail atabilirsiniz, sms gönderebilirsiniz.
#
#                 # alım yapabilirsiniz (0.1 miktarında market ya da limit alım emri girebiliriz):
#
#                 # buy_order = connection.client.order_market_buy(
#                 #     symbol=symbol,
#                 #     quantity=0.1)