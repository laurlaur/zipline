import pandas as pd
import numpy as np

from datetime import datetime
from zipline.gens.tradegens import DataFrameSource
from zipline import ndict
from zipline.utils.factory import create_trading_environment
from zipline.gens.transform import StatefulTransform
from zipline.lines import SimulatedTrading
from zipline.finance.slippage import FixedSlippage

from logbook import Logger

logger = Logger('Algo')

class BuySellAlgorithm(object):
    """Algorithm that buys and sells alternatingly. The amount for
    each order can be specified. In addition, an offset that will
    quadratically reduce the amount that will be bought can be
    specified.

    This algorithm is used to test the parameter optimization
    framework. If combined with the UpDown trade source, an offset of
    0 will produce maximum returns.

    """

    def __init__(self, sid, amount, offset):
        self.sid = sid
        self.amount = amount
        self.incr = 0
        self.done = False
        self.order = None
        self.frame_count = 0
        self.portfolio = None
        self.buy_or_sell = -1
        self.offset = offset
        self.orders = []
        self.prices = []

    def initialize(self):
        pass

    def set_order(self, order_callable):
        self.order = order_callable

    def set_portfolio(self, portfolio):
        self.portfolio = portfolio

    def handle_data(self, frame):
        order_size = self.buy_or_sell * (self.amount - (self.offset**2))
        self.order(self.sid, order_size)

        #sell next time around.
        self.buy_or_sell *= -1

        self.orders.append(order_size)

        self.frame_count += 1
        self.incr += 1

    def get_sid_filter(self):
        return [self.sid]

# Algorithm base class, user algorithms inherit from this as they
# don't want to have to copy and know about set_order and
# set_portfolio
class TradingAlgorithm(object):
    def _setup(self):
        assert hasattr(self, 'source'), 'source not set.'
        assert hasattr(self, 'sids'), "sids not set."

        environment = create_trading_environment(start=self.data.index[0], end=self.data.index[-1])

        # Create transforms by wrapping them into StatefulTransforms
        transforms = []
        if hasattr(self, 'registered_transforms'):
            for namestring, trans_descr in self.registered_transforms.iteritems():
                sf = StatefulTransform(
                    trans_descr['class'],
                    *trans_descr['args'],
                    **trans_descr['kwargs']
                )
                sf.namestring = namestring

                transforms.append(sf)


        self.simulated_trading = SimulatedTrading(
            [self.source],
            transforms,
            self,
            environment,
            FixedSlippage()
        )

    def _create_daily_stats(self, perfs):
        # create daily stats dataframe
        daily_perfs = []
        cum_perfs = []
        for perf in perfs:
            if 'daily_perf' in perf:
                daily_perfs.append(perf['daily_perf'])
            else:
                cum_perfs.append(perf)

        daily_dts = [np.datetime64(perf['period_close'], utc=True) for perf in daily_perfs]
        daily_stats = pd.DataFrame(daily_perfs, index=daily_dts)

        return daily_stats

    def run(self, data, compute_risk_metrics=False):
        self.source = DataFrameSource(data, sids=self.sids)
        self.data = data
        self._setup()

        # drain simulated_trading
        perfs = []
        for perf in self.simulated_trading:
            #from nose.tools import set_trace; set_trace()
            perfs.append(perf)

        #perfs = list(self.simulated_trading)

        daily_stats = self._create_daily_stats(perfs)
        return daily_stats

    def set_portfolio(self, portfolio):
        self.portfolio = portfolio

    def set_order(self, order_callable):
        self.order = order_callable

    def get_sid_filter(self):
        return self.sids

    def set_logger(self, logger):
        self.logger = logger

    def initialize(self):
        pass

    def set_slippage_override(self, slippage_callable):
        pass

    def add_transform(self, transform_class, tag, *args, **kwargs):
        if not hasattr(self, 'registered_transforms'):
            self.registered_transforms = {}

        self.registered_transforms[tag] = {'class': transform_class,
                                           'args': args,
                                           'kwargs': kwargs}


class BuySellAlgorithmNew(TradingAlgorithm):
    """Algorithm that buys and sells alternatingly. The amount for
    each order can be specified. In addition, an offset that will
    quadratically reduce the amount that will be bought can be
    specified.

    This algorithm is used to test the parameter optimization
    framework. If combined with the UpDown trade source, an offset of
    0 will produce maximum returns.

    """

    def __init__(self, sids, amount, offset):
        self.sids = sids
        self.amount = amount
        self.incr = 0
        self.done = False
        self.order = None
        self.frame_count = 0
        self.portfolio = None
        self.buy_or_sell = -1
        self.offset = offset
        self.orders = []
        self.prices = []

    def handle_data(self, data):
        order_size = self.buy_or_sell * (self.amount - (self.offset**2))
        self.order(self.sids[0], order_size)
        logger.debug("ordering" + str(order_size))

        #sell next time around.
        self.buy_or_sell *= -1

        self.orders.append(order_size)

        self.frame_count += 1
        self.incr += 1

