import svi_read_data as wind_data
from hedging_utility import get_spot_price,hedging_performance,calculate_cash_position,calculate_delta_svi,calculate_delta_formula_svi,get_local_volatility_surface_smoothed,calculate_delta_sviVolSurface,calculate_hedging_error,get_local_volatility_surface
from utilities import convert_datelist_from_datetime_to_ql as to_ql_dates
from utilities import convert_datelist_from_ql_to_datetime as to_dt_dates
from utilities import convert_date_from_ql_to_datetime as to_dt_date
from utilities import convert_date_from_datetime_to_ql as to_ql_date
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import QuantLib as ql
import pandas as pd
import math
import numpy as np
from WindPy import w
import datetime
import timeit
import os
import pickle


start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()

def Date(d,m,y):
    return ql.Date(d,m,y)
'''
with open(os.getcwd()+'/intermediate_data/hedging_daily_params_pcprates.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_dates_pcprates.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_daily_svi_dataset_pcprates.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
'''
with open(os.getcwd()+'/intermediate_data/hedging_daily_params_calls.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_dates_calls.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_daily_svi_dataset_calls.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-10]):
    try:
        print(idx_date)
        calibrate_date2 = to_ql_date(dates[idx_date])
        calibrate_date1 = to_ql_date(dates[idx_date+1])
        calibrate_date = to_ql_date(dates[idx_date+2])
        hedge_date = to_ql_date(dates[idx_date+3])
        liquidition_date = to_ql_date(dates[idx_date+4])

        # Liquidition Date Dataset
        dataset_on_liquidition_date = daily_svi_dataset.get(to_dt_date(liquidition_date))
        cal_vols, put_vols, maturity_dates, spot, rf_pcprs = dataset_on_liquidition_date

        # SELECT CALL OPTION DATA!!
        expiration_dates = to_ql_dates(maturity_dates)
        orgnized_data_liquidition_date = svi_util.orgnize_data_for_hedging(
            liquidition_date , daycounter, cal_vols, expiration_dates, spot)
        optiontype = ql.Option.Call

        # Hedge Date Data Set
        dataset_on_hedge_date = daily_svi_dataset.get(to_dt_date(hedge_date))
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, pcprs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, cal_vols_h, expiration_dates_h, spot_on_hedge_date)

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        calibrated_params1 = daily_params.get(to_dt_date(calibrate_date1))  # on calibrate_date
        calibrated_params2 = daily_params.get(to_dt_date(calibrate_date2))  # on calibrate_date
        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)

        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))

        calibrated_params_list=[calibrated_params,calibrated_params1,calibrated_params2]
        calibrate_dates = [calibrate_date,calibrate_date1,calibrate_date2]
        black_var_surface = get_local_volatility_surface_smoothed(calibrated_params_list,to_ql_dates(maturity_dates_c),
                                                                  calibrate_dates,daycounter,calendar,spot_c,rf_c)
        #black_var_surface = get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)

        hedge_error_Ms = {}
        hedge_error_pct_Ms = {}
        for nbr_month in range(4):
            params_Mi = calibrated_params[nbr_month]
            rf_on_hedge_date = pcprs_on_hedge_date.get(nbr_month)
            moneyness_l, strikes_l, close_prices_l, expiration_date_l = orgnized_data_liquidition_date.get(nbr_month)
            moneyness_h, strikes_h, close_prices_h, expiration_date_h = orgnized_data_hedge_date.get(nbr_month)
            rf = curve_on_hedge_date.zeroRate(liquidition_date, daycounter, ql.Continuous).rate()
            hedge_errors = []
            hedge_errors_pct = []
            moneyness = []
            print('liquidition date : ', liquidition_date, ',', nbr_month)
            for idx_k,k in enumerate(strikes_h):
                if k in close_prices_l.keys():
                    close_l = close_prices_l.get(k)
                else:
                    print('strike not found in L date')
                    continue
                close_h = close_prices_h.get(k)
                # No arbitrage condition
                ttm = daycounter.yearFraction(hedge_date,expiration_date_h)
                if close_h < spot_on_hedge_date - k*math.exp(-rf_on_hedge_date*ttm):
                    continue
                delta = calculate_delta_sviVolSurface(black_var_surface,hedge_date,daycounter,calendar,params_Mi,spot,rf,k,expiration_date_h,optiontype)

                print('delta : ',delta)
                cash_on_hedge_date = calculate_cash_position(hedge_date, close_h, spot_on_hedge_date, delta)
                print('cash position : ', cash_on_hedge_date)
                hedge_error = calculate_hedging_error(hedge_date,liquidition_date,
                                                      daycounter,spot,close_l,delta,cash_on_hedge_date,rf)

                hedge_error_pct = hedge_error/close_h
                hedge_error = round(hedge_error,4)
                hedge_error_pct = round(hedge_error_pct, 4)
                hedge_errors.append(hedge_error)
                hedge_errors_pct.append(hedge_error_pct)
                moneyness.append(round(spot_on_hedge_date/k,4))
            print('moneyness : ',moneyness)
            print('hedge errors pct : ', hedge_errors_pct)
            hedge_error_Ms.update({nbr_month:[moneyness,hedge_errors]})
            hedge_error_pct_Ms.update({nbr_month:[moneyness,hedge_errors_pct]})
        if idx_date != 0:
            #print('liquidition date : ',liquidition_date)
            #print('hedge errors pct : ',hedge_error_pct_Ms)
            key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
            daily_hedge_errors.update({key_date1: hedge_error_Ms})
            daily_pct_hedge_errors.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()
print('calibration time : ',stop-start)

#print('daily_hedge_errors = ',daily_hedge_errors)
#print('daily_pct_hedge_errors = ',daily_pct_hedge_errors)
with open(os.getcwd()+'/intermediate_data/hedging_daily_hedge_errors_svi_call.pickle','wb') as f:
    pickle.dump([daily_hedge_errors,daily_pct_hedge_errors],f)


mny_0,mny_1,mny_2,mny_3 = hedging_performance(daily_pct_hedge_errors,daily_pct_hedge_errors.keys())
print("="*100)
print("SVI Model Average Hedging Percent Error,CALL (SVI VOL SURFACE 3-Day SMOOTHING) : ")
print("="*100)
print("%20s %20s %30s" % ("contract month","moneyness", "avg hedging error(%)"))
print("-"*100)
for i in range(4):
    if len(mny_0.get(i)) > 0: print("%20s %20s %25s" % (i,' < 0.97',round(sum(mny_0.get(i))*100/len(mny_0.get(i)),4)))
    if len(mny_1.get(i))>0: print("%20s %20s %25s" % (i,' 0.97 - 1.00', round(sum(mny_1.get(i))*100 / len(mny_1.get(i)),4)))
    if len(mny_2.get(i)) > 0: print("%20s %20s %25s" % (i,' 1.00 - 1.03', round(sum(mny_2.get(i))*100 / len(mny_2.get(i)),4)))
    if len(mny_3.get(i)) > 0: print("%20s %20s %25s" % (i,' > 1.03', round(sum(mny_3.get(i))*100 / len(mny_3.get(i)),4)))
    print("-" * 100)
print('total date : ', len(daily_pct_hedge_errors.keys()))
print(daily_pct_hedge_errors.keys())