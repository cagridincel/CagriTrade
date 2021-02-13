import sqlite3 as conn
from datetime import datetime

Db = conn.connect("tradeDatabase.db")

cs = Db.cursor()

# cs.execute("create table Trader (TransactionStatus TEXT, IndicatorName TEXT, Symbol TEXT, isactive TEXT, expense real, bought_price real, quantity real, bought_time real,
# sold_price REAL, sold_time REAL, closed_total real, profit real)")

# cs.execute("create table SignalLogs (TransactionType TEXT, IndicatorName TEXT, Symbol TEXT,price REAL, time TEXT )")
# cs.execute("insert into SignalLogs values (?, ?)",("Knight",1234,))

symbol = 'VIBBTC'
price = 0.00000252

cs.execute(
    """select * from Trader where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 'TILLSON'""" % (symbol))
dataSet = cs.fetchone()
if dataSet is not None:
    print("as")
    quant = float(dataSet[6])
    ex = float(dataSet[4])
    closed_total = float(quant * price)
    print(closed_total)
    prof = float(closed_total - ex)
    cs.execute(""" Update Trader set TransactionStatus = 'COMPLETED', sold_price = '%s', sold_time = '%s', 
    closed_total = '%s', profit = '%s'   where symbol = '%s' and isactive = 'ACTIVE' and IndicatorName = 
    'TILLSON'""" % (price, datetime.now(), closed_total, prof,symbol))
    Db.commit()


else:
    print("boş")
    # cs.execute("insert into Trader values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #            ("BUY", "TILLSON", symbol, "ACTIVE", 100, price, 100 / float(price), datetime.now(), None, None, None,
    #             None))
    Db.commit()
