import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class Backtest:

    def __init__(self, sign, return_data):
        '''

        :param sign: the dataframe of 0-1 signal
        :param return_data: the return data of the index/stock
        '''

        self.sign = sign
        self.return_data = return_data

    def get_return_for_test(self):
        '''

        :return: two columns with one is the true return data and the other one is the construct return data
        '''

        self.use_return = self.return_data.loc[list(self.sign.index), :]
        self.use_return.columns = ['return_true']
        self.construct_return = (self.use_return['return_true'] * self.sign['signal']).to_frame()
        self.construct_return.columns = ['return_construct']
        self.outcome = pd.concat([self.use_return, self.construct_return], axis = 1)

        return self.outcome

    def get_nav_and_plot(self, pic_name):
        '''

        calculate nav and plot

        :param pic_name: the title of the nav picture
        '''

        self.nav_compare = self.outcome.apply(lambda x: (1 + x).cumprod())
        self.nav_compare.columns = ['true', 'construct']
        self.nav_compare.plot(legend = ['true', 'construct'])
        plt.title(pic_name)
        plt.show()
        return self.nav_compare

    def get_sharpe_compare(self, risk_free_rate = 0.015, trading_days_per_year = 243):
        '''

        calculate annualized sharpe ratio
        '''

        r = risk_free_rate
        sharpe = (self.outcome.apply(
            lambda x: (x.mean() * trading_days_per_year - r) / (x.std() * np.sqrt(trading_days_per_year)))).to_frame()
        sharpe.columns = ['sharpe']
        sharpe.index = ['true', 'construct']
        return sharpe

    def get_annualized_return_compare(self, trading_days = 243):
        '''

        calculate annualized return
        '''

        a_r = (self.outcome.apply(lambda x: x.mean() * trading_days)).to_frame()
        a_r.columns = ['annualized_return']
        a_r.index = ['true', 'construct']

        return a_r

    def get_max_drawdown_compare(self):
        '''

        calculate the max drawdown
        '''

        max_draw = (
            self.nav_compare.apply(lambda x: ((x.expanding().max() - x) / x.expanding().max()).max())).to_frame()
        max_draw.columns = ['max_draw']
        max_draw.index = ['true', 'construct']

        return max_draw

    def get_gross_return_compare(self):
        '''

        calculate the gross return
        '''

        gross_return = (self.nav_compare.apply(lambda x: x[-1] / x[0])).to_frame()
        gross_return.columns = ['gross_return']
        gross_return.index = ['true', 'construct']
        return gross_return

    def get_win_rate_compare(self):
        '''

        calculate the win rate
        '''

        w_r = (self.outcome.apply(lambda x: len(x[x > 0]) / len(x[x != 0]))).to_frame()
        w_r.columns = ['win_rate']
        w_r.index = ['true', 'construct']
        w_r.iloc[0, 0] = np.nan
        return w_r

    def get_trading_times_compare(self):
        '''

        calculate the trading times during all the test period
        '''

        trading_sig = self.sign.add(self.sign.shift(-1))
        t_t = pd.DataFrame(index = ['construct'], data = len(trading_sig[trading_sig['signal'] == 1]),
                           columns = ['trading_times'])
        return t_t

    def get_all_evaluation_compare(self, risk_free_rate, pic_name, threshold, method):
        '''

        :param method: split, rolling or expanding window.
        '''

        self.get_return_for_test()
        self.get_nav_and_plot(pic_name)
        sharpe = self.get_sharpe_compare(risk_free_rate)
        a_r = self.get_annualized_return_compare()
        g_r = self.get_gross_return_compare()
        m_d = self.get_max_drawdown_compare()
        w_r = self.get_win_rate_compare()
        t_t = self.get_trading_times_compare()
        evaluation = pd.concat([sharpe, a_r, g_r, m_d, w_r, t_t], join = 'outer', axis = 1)
        evaluation.index.name = ('type')
        evaluation['method'] = 'Threshold = ' + str(threshold) + ', Method = ' + method
        evaluation.loc['true', 'method'] = 'Benchmark'
        evaluation = evaluation.reset_index(drop = False).set_index(['method'])

        return evaluation
