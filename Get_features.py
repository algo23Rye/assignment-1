import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')


class Feature_calculation:

    def __init__(self, data):
        '''

        :param data: a dataframe contains close price
        '''

        self.data = data

    def return_calculation(self):
        '''

        :return: a dataframe with return columns
        '''

        self.data['return'] = (self.data['close'] - self.data['close'].shift(1)) / self.data['close'].shift(1)
        self.data.dropna(inplace = True)
        return self.data

    def get_holding_return(self, n = 10):
        '''

        :param n: the length of the holding period, in the paper is 10 days
        :return: the feature :a dataframe
        '''

        holding_return = (self.data['close'].rolling(n).apply(lambda x: (x[-1] - x[0]) / x[0])).to_frame()
        holding_return.columns = ['holding_return_' + str(n) + "_days"]
        holding_return.dropna(inplace = True)
        return holding_return

    def get_mean_return(self, n = 5):
        '''

        :param n: mean daily return of n days
        '''

        mean_return = (self.data['return'].rolling(n).mean()).to_frame()
        mean_return.dropna(inplace = True)
        mean_return.columns = ['mean_return_' + str(n) + "_days"]
        return mean_return

    def get_holding_sharpe(self, risk_free_rate = 0.015, n = 10):
        '''

        :param risk_free_rate: the annulized risk_free rate
        :param n: the holding period (days)
        '''

        r_10 = risk_free_rate / 365 * n
        holding_return = self.data['close'].rolling(n).apply(lambda x: (x[-1] - x[0]) / x[0])
        holding_std = self.data['return'].rolling(n).std() * np.sqrt(n)
        holding_sharpe = ((holding_return - r_10) / holding_std).to_frame()
        holding_sharpe.dropna(inplace = True)
        holding_sharpe.columns = ['holding_sharpe_' + str(n) + "_days"]
        return holding_sharpe

    def get_volume_ratio(self, n1 = 10, n2 = 5):
        '''

        :param n1: numerator:n1 days mean volume
        :param n2: denominator: n2 days mean volume
        '''

        n1_sum_v = self.data['volume'].rolling(n1).mean()
        n2_sum_v = self.data['volume'].rolling(n2).mean()
        ratio = (n2_sum_v / n1_sum_v).to_frame()
        ratio.dropna(inplace = True)
        ratio.columns = [str(n2) + "_" + str(n1) + "_volume ratio"]
        return ratio

    def get_all_features(self):
        '''

        merge all the features
        '''

        self.return_calculation()
        holding_return = self.get_holding_return()
        mean_return = self.get_mean_return()
        holding_sharpe = self.get_holding_sharpe()
        ratio = self.get_volume_ratio()
        all_features = pd.concat([holding_return, mean_return, holding_sharpe, ratio], join = 'inner', axis = 1)

        return all_features

    def features_plot(self, all_features, pic_name):
        '''

        draw histograms  of the features

        :param all_features: a dataframe of features without being standardized
        :param pic_name: the title of the picture
        '''

        plt.figure(figsize = (16, 8))
        for i in range(len(all_features.columns)):
            name = all_features.columns[i]
            plt.subplot(2, 2, i + 1)
            all_features[name].hist(bins = 40, density = True)
            all_features[name].plot(kind = 'kde')
            plt.title(name)
            plt.suptitle(pic_name, fontsize = 20)
        plt.show()

    def features_z_score_standardize(self, all_features):
        '''

        :param all_features: a dataframe of features without being standardized
        :return: standardized features using rolling and z_score method
        '''

        s_features = all_features.apply(lambda x: (x - x.expanding().mean()) / x.expanding().std())
        s_features.dropna(inplace = True)
        # drop the first 100, because this is a rolling standardization
        s_features = s_features.iloc[100:, :]
        return s_features

    def get_obj(self, n = 10):
        '''

        in the paper the objective is the sign of return of the holding period (future n days)

        :param n: the holding period (n days) of return
        :return: the objective to be predicted
        '''

        future_return = (self.data['close'].shift(-n + 1).rolling(n).apply(lambda x: (x[-1] - x[0]) / x[0])).to_frame()
        future_return.columns = ['future_holding_return_' + str(n) + "_days"]
        future_return.shift(-2).dropna(inplace = True)  # return calculated from T+2, because enter the market at T+1
        future_return['objective'] = 0
        future_return['objective'].loc[future_return['future_holding_return_' + str(n) + "_days"] > 0] = 1
        obj = future_return.loc[:, ['objective']]
        return obj
