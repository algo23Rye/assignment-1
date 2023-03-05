from Get_data import Get_data
from Get_features import Feature_calculation
from Logistic_prediction import Prediction
from Backtest import Backtest
import pandas as pd


def Get_outcome(index_code, index_name, path = "./"):
    # First, download the data
    get_data = Get_data(path, end_date = '20230303')
    df = get_data.get_index_data(index_code)

    # store the data
    df.to_csv(path + index_code + ".csv", encoding = 'gbk')

    # Second, get the features
    data = pd.read_csv(path + index_code + ".csv", usecols = ['date', 'code', 'close', 'volume'],
                       index_col = ['date'],
                       encoding = 'gbk', parse_dates = True)
    fc = Feature_calculation(data)
    all_features = fc.get_all_features()

    # plot the four features
    fc.features_plot(all_features, index_name)

    # get the z_score standardized features
    s_features = fc.features_z_score_standardize(all_features)

    # get the objective
    obj = fc.get_obj()

    # Then, predict
    all_data = pd.concat([s_features, obj], join = 'inner', axis = 1)
    risk_free_rate = 0.015

    rolling_period_list = [90, 120]

    threshold_list = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7]
    pre = Prediction()
    return_data = fc.data.loc[:, ['return']]

    evaluation_all = pd.DataFrame()

    # for 3:2 split the data to train data and test data
    for threshold in threshold_list:
        sign1 = pre.logistic_reg_split(all_data, threshold)
        bt = Backtest(sign1, return_data)
        eval = bt.get_all_evaluation_compare(risk_free_rate, '3:2 split data, threshold = ' + str(threshold),
                                             threshold,
                                             '3:2 split data')
        evaluation_all = pd.concat([evaluation_all, eval])

    # rolling window method
    # To compare them in the same period
    start_date = sign1.index.values[0]
    for rolling_period in rolling_period_list:
        for threshold in threshold_list:
            sign2 = pre.logistic_reg_rolling(all_data.loc['2015':, :], rolling_period, threshold)
            sign2 = sign2.loc[start_date:, :]
            bt = Backtest(sign2, return_data)
            eval = bt.get_all_evaluation_compare(risk_free_rate, 'Rolling window of ' + str(
                rolling_period) + ' days, threshold = ' + str(
                threshold), threshold, 'Rolling window of ' + str(rolling_period) + ' days')
            evaluation_all = pd.concat([evaluation_all, eval])

    #expanding window method
    # start the same date as the split method
    starting_period = int(len(all_data) * 0.6) + 1
    for threshold in threshold_list:
        sign3 = pre.logistic_reg_expanding(all_data, starting_period, threshold)
        sign3 = sign3.loc[start_date:, :]
        bt = Backtest(sign3, return_data)
        eval = bt.get_all_evaluation_compare(risk_free_rate, 'Expanding window, threshold = ' + str(threshold),
                                             threshold, 'Expanding window')
        evaluation_all = pd.concat([evaluation_all, eval])

    evaluation_all.drop_duplicates(inplace = True)
    evaluation_all.to_csv('outcome for ' + index_name + '.csv', encoding = 'gbk')

    return evaluation_all


if __name__ == '__main__':
    index_code = '000300'
    index_name = 'CSI300'
    path = "./"
    evaluation = Get_outcome(index_code, index_name, path)
