import datetime
import QuantLib as ql
import hashlib
import pandas as pd

class BktUtil():

    def __init__(self):

        self.long = 1
        self.short = -1
        self.neutrual = 0
        self.long_top = 1
        self.long_bottom = -1
        self.nan_value = -999.0
        self.type_call = 'call'
        self.type_put = 'put'
        self.type_all = 'all'
        self.method_1 = 0
        self.method_2 = 1
        self.cd_frequency_low = ['daily','weekly','monthly','yearly']
        self.cd_frequency_intraday = ['1min','5min']

        """database column names"""

        self.col_date = 'dt_date'
        self.col_datetime = 'dt_datetime'
        self.col_maturitydt = 'dt_maturity'

        self.col_code_instrument = 'code_instrument'
        self.col_id_instrument = 'id_instrument'
        self.col_id_underlying = 'id_underlying'
        self.col_option_type = 'cd_option_type'
        self.col_name_contract_month = 'name_contract_month'
        self.col_strike = 'amt_strike'
        self.col_adj_strike = 'amt_adj_strike'
        self.col_close = 'amt_close'
        self.col_open = 'amt_open'
        self.col_adj_option_price = 'amt_adj_option_price'
        self.col_option_price = 'amt_option_price'
        self.col_underlying_close = 'amt_underlying_close'
        self.col_underlying_open_price = 'amt_underlying_open_price'
        self.col_settlement = 'amt_settlement'
        self.col_last_settlement = 'amt_last_settlement'
        self.col_last_close = 'amt_last_close'
        self.col_multiplier = 'nbr_multiplier'
        self.col_holding_volume = 'amt_holding_volume'
        self.col_trading_volume = 'amt_trading_volume'
        self.col_morning_open_15min = 'amt_morning_open_15min'
        self.col_morning_close_15min = 'amt_morning_close_15min'
        self.col_afternoon_open_15min = 'amt_afternoon_open_15min'
        self.col_afternoon_close_15min = 'amt_afternoon_close_15min'
        self.col_morning_avg = 'amt_morning_avg'
        self.col_afternoon_avg = 'amt_afternoon_avg'
        self.col_daily_avg = 'amt_daily_avg'
        self.col_implied_vol = 'pct_implied_vol'
        self.col_delta = 'amt_delta'
        self.col_theta = 'amt_theta'
        self.col_vega = 'amt_vega'
        self.col_rho = 'amt_rho'
        self.col_carry = 'amt_carry'
        self.col_iv_roll_down = 'amt_iv_roll_down'

        self.nbr_invest_days='nbr_invest_days'
        self.col_rf = 'risk_free_rate'



        """output dataframe column names"""

        self.id_position='id_position'
        self.id_instrument='id_instrument'
        self.multiplier='multiplier'
        self.mkt_price = 'mkt_price'
        self.dt_open='dt_open'
        self.long_short='long_short'
        self.open_price='open_price'
        self.premium='premium'
        # self.open_trading_cost='open_trading_cost'
        self.unit='unit'
        self.npv='npv'
        self.margin_capital='margin_capital'
        self.dt_close='dt_close'
        self.days_holding='days_holding'
        self.close_price='close_price'
        # self.close_trading_cost='close_trading_cost'
        self.realized_pnl='realized_pnl'
        self.unrealized_pnl='unrealized_pnl'
        self.flag_open = 'flag_open'

        self.dt_date='dt_date'
        self.nbr_trade='nbr_trade'
        self.margin_capital='margin_capital'
        self.mkm_pnl='mkm_pnl'
        self.realized_pnl='realized_pnl'
        # self.mkm_portfolio_value='mkm_portfolio_value'
        self.mtm_short_positions = 'mtm_short_positions'
        self.mtm_long_positions = 'mtm_long_positions'

        self.cash='cash'
        self.money_utilization='money_utilization'
        self.total_asset = 'total_asset'
        self.npv = 'npv'
        self.benchmark = 'benchmark'

        self.dt_trade = 'dt_trade'
        self.trading_type='trading_type'
        self.trade_price='trade_price'
        self.trading_cost='trading_cost'
        self.bktoption = 'bktoption'


        self.tb_columns = [
                           self.id_instrument,
                           self.multiplier,
                           self.mkt_price,
                           self.dt_open,
                           self.long_short,
                           self.open_price,
                           self.premium,
                           # self.open_trading_cost,
                           self.unit,
                           self.margin_capital,
                           self.dt_close,
                           self.days_holding,
                           self.close_price,
                           # self.close_trading_cost,
                           self.realized_pnl,
                           self.unrealized_pnl,
                           self.flag_open]

        self.account_columns = [self.dt_date,
                                self.npv,
                                self.nbr_trade,
                                self.margin_capital,
                                self.realized_pnl,
                                self.unrealized_pnl,
                                self.mtm_long_positions,
                                self.mtm_short_positions,
                                self.cash,
                                self.money_utilization,
                                self.total_asset,
                                ]

        self.record_columns = [self.dt_trade,
                               self.id_instrument,
                               self.trading_type,
                               self.trade_price,
                               self.trading_cost,
                               self.unit]

    def to_ql_date(self,date):
        return ql.Date(date.day,date.month,date.year)

    def to_dt_date(self,ql_date):
        return datetime.date(ql_date.year(),ql_date.month(),ql_date.dayOfMonth())

    def fun_option_price(self,df):
        if df[self.col_close] != self.nan_value:
            option_price = df[self.col_close]
        elif df[self.col_settlement] != self.nan_value:
            option_price = df[self.col_settlement]
        else:
            print('amt_close and amt_settlement are null!')
            print(df)
            option_price = None
        return option_price

    def get_df_by_mdt_type(self, df, mdt, option_type):
        if option_type == self.type_call:
            return self.get_df_call_by_mdt(mdt, df)
        elif option_type == self.type_put:
            return self.get_df_put_by_mdt(mdt, df)
        else:
            return "Unsupport Option Type!"

    def get_df_by_type(self, df, option_type):
        if option_type == self.type_call:
            c = df[self.col_option_type] == self.type_call
        elif option_type == self.type_put:
            c = df[self.col_option_type] == self.type_put
        else:
            return "Unsupport Option Type!"
        df = df[c].reset_index(drop=True)
        return df

    def get_df_by_mdt(self, df, mdt):
        c = df[self.col_maturitydt] == mdt
        df = df[c].reset_index(drop=True)
        return df

    def get_df_call_by_mdt(self, df, mdt):
        c = (df[self.col_option_type] == self.type_call) & (df[self.col_maturitydt] == mdt)
        df = df[c].reset_index(drop=True)
        return df

    def get_df_put_by_mdt(self, df, mdt):
        c = (df[self.col_option_type] == self.type_put) & (df[self.col_maturitydt] == mdt)
        df = df[c].reset_index(drop=True)
        return df

    """ 50ETF期权分红后会产生同样行权价的两个期权，选择trading volume较大的一个。 """
    def get_duplicate_strikes_dropped(self, df_daily_state):
        maturities = sorted(df_daily_state[self.col_maturitydt].unique())
        df = pd.DataFrame()
        for mdt in maturities:
            df_mdt_call = df_daily_state[(df_daily_state[self.col_maturitydt] == mdt) &
                                     (df_daily_state[self.col_option_type] == self.type_call)] \
                .sort_values(by=self.col_trading_volume, ascending=False) \
                .drop_duplicates(subset=[self.col_adj_strike])
            df_mdt_put = df_daily_state[(df_daily_state[self.col_maturitydt] == mdt) &
                                    (df_daily_state[self.col_option_type] == self.type_put)] \
                .sort_values(by=self.col_trading_volume, ascending=False) \
                .drop_duplicates(subset=[self.col_adj_strike])
            df = df.append(df_mdt_call, ignore_index=True)
            df = df.append(df_mdt_put, ignore_index=True)
        return df

    def dividend_dates(self):
        """ 分红日前，使用调整前的行权价计算隐含波动率，例如，
        分红日d1影响的合约'1612','1701','1703','1706'在分红日前需反算adj_strike,之后则不需要"""
        d1 = datetime.date(2016,11,29)
        d2 = datetime.date(2017,11,28)
        res = {d1:['1612','1701','1703','1706'],d2:['1712','1801','1803','1806']}
        return res

    def get_applicable_strike(self,bktoption):
        if bktoption.multiplier() == 10000 :
            return bktoption.strike() #非调整的合约直接去行权价
        eval_date = bktoption.eval_date
        contract_month = bktoption.contract_month()
        dict = self.dividend_dates()
        dates = sorted(dict.keys(),reverse=False)
        if eval_date < dates[0]:
            return bktoption.adj_strike() #分红除息日前反算调整前的行权价
        elif eval_date < dates[1]:
            if contract_month in dict[dates[1]]:
                return bktoption.adj_strike() #分红除息日前反算调整前的行权价
            else:
                return bktoption.strike()  # 分红除息日后用实际调整后的行权价
        else:
            return bktoption.strike() # 分红除息日后用实际调整后的行权价


    def get_sha(self):

        sha = hashlib.sha256()
        now = str(datetime.datetime.now()).encode('utf-8')
        sha.update(now)
        id_position = sha.hexdigest()
        return id_position


















