from binance.client import Client
import talib as ta
import numpy as np
from datetime import datetime
import sys
import math

class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """

    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)

def generateTillsonT3(close_array, high_array, low_array, volume_factor, t3Length):

    ema_first_input = (high_array + low_array + 2 * close_array) / 4

    e1 = ta.EMA(ema_first_input, t3Length)

    e2 = ta.EMA(e1, t3Length)

    e3 = ta.EMA(e2, t3Length)

    e4 = ta.EMA(e3, t3Length)

    e5 = ta.EMA(e4, t3Length)

    e6 = ta.EMA(e5, t3Length)

    c1 = -1 * volume_factor * volume_factor * volume_factor

    c2 = 3 * volume_factor * volume_factor + 3 * volume_factor * volume_factor * volume_factor

    c3 = -6 * volume_factor * volume_factor - 3 * volume_factor - 3 * volume_factor * volume_factor * volume_factor

    c4 = 1 + 3 * volume_factor + volume_factor * volume_factor * volume_factor + 3 * volume_factor * volume_factor

    T3 = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

    return T3


