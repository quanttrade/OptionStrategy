# encoding: utf-8

import datetime

from WindPy import w

from Utilities import admin_write_util as admin
from data_access.db_data_collection import DataCollection

"""
batch insert option daily data
"""

w.start()

conn = admin.conn_gc()

options_mktdata_daily = admin.table_options_mktdata()

dc = DataCollection()

today = datetime.date.today()
beg_date = datetime.date(2019, 1, 1)
end_date = datetime.date.today()

date_range = w.tdays(beg_date, end_date, "").Data[0]
date_range = sorted(date_range, reverse=True)
for dt in date_range:
    db_data = dc.table_options().wind_cu_option(dt.strftime("%Y-%m-%d"))
    # db_data = dc.table_options().wind_data_50etf_option(dt.strftime("%Y-%m-%d"))
    if len(db_data) == 0: print('no data')
    for res in db_data:
        try:
            conn.execute(options_mktdata_daily.insert(), res)
            print(res)
        except Exception as e:
            print(e)
