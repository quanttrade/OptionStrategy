from back_test.model.base_option_set import BaseOptionSet
from data_access.get_data import get_50option_mktdata, get_comoption_mktdata
import back_test.model.constant as c
import datetime
from PricingLibrary.BinomialModel import BinomialTree
import Utilities.admin_write_util as admin
import numpy as np

start_date = datetime.date(2018, 7, 14)
end_date = datetime.date(2018, 8, 9)
init_vol = 0.2
rf = 0.03
steps = 1000

""" namecode : M """
table_iv = admin.table_implied_volatilities()
df_metrics = get_comoption_mktdata(start_date, end_date,c.Util.STR_SR)
exercise_type = c.OptionExerciseType.AMERICAN
optionset = BaseOptionSet(df_metrics)
optionset.init()
dt_maturity = optionset.select_maturity_date(0,min_holding=8)
spot = optionset.get_underlying_close(maturitydt=dt_maturity)
list_res = []
m  = optionset.df_maturity_and_contract_months
while optionset.has_next():
    call_list, put_list = optionset.get_options_list_by_moneyness_mthd1(moneyness_rank=0, maturity=dt_maturity)
    # print(call_list)
    # print(put_list)
    print(optionset.eval_date, dt_maturity)
    print('spot : ',spot)
    base_option_call = call_list[0]
    print(base_option_call)

    # binomial_tree = BinomialTree(
    #     base_option_call.eval_date,
    #     base_option_call.maturitydt(),
    #     base_option_call.option_type(),
    #     exercise_type,
    #     spot,base_option_call.strike(),vol=init_vol,rf=rf,n=1000)
    # (iv_call, estimated_call) = binomial_tree.estimate_vol(base_option_call.mktprice_close())
    #
    # print(iv_call)
    #
    # list_res.append( {
    #     'dt_date':base_option_call.eval_date,
    #     'id_underlying':base_option_call.id_underlying(),
    #     'cd_option_type':'call',
    #     'cd_mdt_selection':'hp_8_1st',
    #     'cd_atm_criterion':'nearest_strike',
    #     'nbr_moneyness':0,
    #     'id_instrument':base_option_call.id_instrument(),
    #     'dt_maturity':dt_maturity,
    #     'pct_implied_vol':iv_call,
    #     'amt_close':float(base_option_call.mktprice_close()),
    #     'amt_strike':float(base_option_call.strike()),
    #     'amt_applicable_strike':float(base_option_call.strike()),
    #     'amt_underlying_close':float(spot)
    # })
    base_option_put = put_list[0]
    print(base_option_put)

    # binomial_tree = BinomialTree(
    #     base_option_put.eval_date,
    #     base_option_put.maturitydt(),
    #     base_option_put.option_type(),
    #     exercise_type,
    #     spot,base_option_put.strike(),vol=init_vol,rf=rf,n=1000)
    # (iv_put, estimated_put) = binomial_tree.estimate_vol(base_option_put.mktprice_close())
    # print(iv_put)
    # list_res.append( {
    #     'dt_date':base_option_put.eval_date,
    #     'id_underlying':base_option_put.id_underlying(),
    #     'cd_option_type':'put',
    #     'cd_mdt_selection':'hp_8_1st',
    #     'cd_atm_criterion':'nearest_strike',
    #     'nbr_moneyness':0,
    #     'id_instrument':base_option_put.id_instrument(),
    #     'dt_maturity':dt_maturity,
    #     'pct_implied_vol':iv_put,
    #     'amt_close':float(base_option_put.mktprice_close()),
    #     'amt_strike':float(base_option_put.strike()),
    #     'amt_applicable_strike':float(base_option_put.strike()),
    #     'amt_underlying_close':float(spot)
    # })
    optionset.next()
    dt_maturity = optionset.select_maturity_date(0, min_holding=8)
    spot = optionset.get_underlying_close(maturitydt=dt_maturity)

