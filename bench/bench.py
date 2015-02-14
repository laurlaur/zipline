import datetime as dt
from datetime import  timedelta
import pytz
import pandas as pd
import pstats
import time
import numpy as np
from zipline.utils.tradingcalendar import get_early_closes
from zipline.api import *
import zipline
import cProfile
from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import load_bars_from_yahoo
import os.path

def load_data():
    data_file_name = "data.hdf"
    if os.path.exists(data_file_name):
        data = pd.read_hdf(data_file_name,'data',format='fixed')
        return data

    start = dt.datetime(2010, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = dt.datetime(2014, 1, 2, 0, 0, 0, 0, pytz.utc)
    symbols = ["LUV","VRTX"]
    data = load_bars_from_yahoo(stocks=symbols, start=start, end=end)

    data.to_hdf(data_file_name,'data',format='fixed')
    return data
    # Define algorithm


def initialize(context):
    # Define the instruments in the portfolio:
#    set_symbol_lookup_date("2010-1-1")
    context.sids = {
        symbol("VRTX"):0.09,
        symbol("LUV"):0.08,
        symbol("KR"):0.08,
        symbol("MCK"):0.07,
        symbol("TRW"):0.06,
        symbol("NOC"):0.06,
        symbol("CELG"):0.05,
        symbol("ALL"):0.05,
        symbol("AVGO"):0.04,
        symbol("GPK"):0.04,
        symbol("MNST"):0.04,
        symbol("SEIC"):0.03,
        symbol("LOW"):0.03,
        symbol("COV"):0.03,
        symbol("BX"):0.03,
        symbol("FISV"):0.02,
        symbol("ULTA"):0.02,
        symbol("EFX"):0.01,
        symbol("KRC"):0.01
        }

    # Initialize context variables the define rebalance logic:
    context.rebalance_date = None
    context.next_rebalance_Date = None
    context.rebalance_days = 7

def handle_data(context, data):
    exchange_time = pd.Timestamp(get_datetime()).tz_convert('US/Eastern')
#    order(symbol('AAPL'), 10)

    # If it is rebalance day, rebalance:
    if context.rebalance_date == None or exchange_time >= context.next_rebalance_date:
       # If we are in rebalance window but there are open orders, wait til next minute
       if False == True:
            log.info('Has open orders, not rebalancing.')
       else:
            context.rebalance_date = exchange_time
            context.next_rebalance_date = context.rebalance_date + timedelta(days=context.rebalance_days)
            rebalance(context, data, exchange_time)


def rebalance(context,data,exchange_time):
    for sid in context.sids:
        if sid in data:
            order_target_percent(sid, context.sids[sid])



# handle_data functions
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)

# Run algorithm
data = load_data()
start_time = time.time()
#cProfile.run('algo_obj.run(data)', 'restats')
algo_obj.run(data)
#p = pstats.Stats('restats')
#p.strip_dirs().sort_stats(-1).print_stats()
#p.sort_stats('cumulative').print_stats(20)
#p.sort_stats('time').print_stats(10)


#perf_manual = algo_obj.run(data)
#RiskMetricsCumulative
print "Risk Metrics"
print type(algo_obj.perf_tracker.cumulative_risk_metrics)
#print "Sortine: "+str(algo_obj.perf_tracker.cumulative_risk_metrics.calculate_sortino())
#print "Sharp: "+str(algo_obj.perf_tracker.cumulative_risk_metrics.calculate_sharpe())
print "Max Draw Down: "+str(algo_obj.perf_tracker.cumulative_risk_metrics.calculate_max_drawdown())
print "Return: "+str(algo_obj.perf_tracker.returns)
print "Return: "+str(algo_obj.perf_tracker.cumulative_performance.returns)

print("--- %s seconds ---" + str(time.time() - start_time))