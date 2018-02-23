from back_test.bkt_option_set import BktOptionSet
from back_test.bkt_util import BktUtil
from back_test.data_option import get_50option_mktdata,get_sr_option_mktdata
import QuantLib as ql
from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime



date = datetime.date(2018,2,22)
start_date = datetime.date(2017,1,1)
end_date = datetime.date(2018,2,22)

calendar = ql.China()
daycounter = ql.ActualActual()
util = BktUtil()
engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/metrics', echo=True)
conn = engine.connect()
metadata = MetaData(engine)
optionMetrics = Table('option_metrics', metadata, autoload=True)

df_option_metrics = get_sr_option_mktdata(date,date)

bkt_optionset = BktOptionSet('daily', df_option_metrics, 20)

option_metrics = bkt_optionset.collect_option_metrics()
try:
    for r in option_metrics:
        res = optionMetrics.select((optionMetrics.c.id_instrument == r['id_instrument'])
                                   & (optionMetrics.c.dt_date == r['dt_date'])).execute()
        if res.rowcount > 0:
            optionMetrics.delete((optionMetrics.c.id_instrument == r['id_instrument'])
                                 & (optionMetrics.c.dt_date == r['dt_date'])).execute()
        conn.execute(optionMetrics.insert(), r)
    print('option metrics -- inserted into data base succefully')
except Exception as e:
    print(e)

# df_option_metrics = get_option_mktdata(start_date,end_date)
#
# while bkt_optionset.index < len(bkt_optionset.dt_list):
#     # if bkt_optionset.index == 0:
#     #     bkt_optionset.next()
#     #     continue
#     evalDate = bkt_optionset.eval_date
#
#     if evalDate == bkt_optionset.end_date:
#         break
#     option_metrics = bkt_optionset.collect_option_metrics()
#     try:
#         for r in option_metrics:
#             res = optionMetrics.select((optionMetrics.c.id_instrument == r['id_instrument'])
#                                        &(optionMetrics.c.dt_date == r['dt_date'])).execute()
#             if res.rowcount > 0:
#                 optionMetrics.delete((optionMetrics.c.id_instrument == r['id_instrument'])
#                                        &(optionMetrics.c.dt_date == r['dt_date'])).execute()
#             conn.execute(optionMetrics.insert(), r)
#         print('option metrics -- inserted into data base succefully')
#     except Exception as e:
#         print(e)
#         continue
#     bkt_optionset.next()