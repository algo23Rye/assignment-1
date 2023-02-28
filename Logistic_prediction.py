import pandas as pd
from sklearn.linear_model import LogisticRegression


class Prediction:
    def logistic_reg_split(self, all_data, threshold):
        '''
        simply split the data to train data and test data

        :param all_data: concating data of features and objective
        :param threshold:gi
        :return:
        '''

        logi_reg = LogisticRegression(penalty = 'l2', tol = 0.0001, solver = 'liblinear', C = 1.0, max_iter = 100)
        X, y = all_data.iloc[:, :-1], all_data.iloc[:, -1]
        # follow the papar to get train data
        # 60% of the data to be the train data
        index = int(len(all_data) * 0.6) + 1
        trainX, trainy = X.iloc[:index, :], y.iloc[:index]
        testX, testy = X.iloc[index:, :], y.iloc[index:]
        clf = logi_reg.fit(trainX, trainy)
        prob_for_1 = pd.DataFrame(index = testy.index, columns = ['prob'])
        prob_for_1['prob'] = clf.predict_proba(testX)[:, -1].T
        sign = prob_for_1.copy()
        sign['prob'] = 0
        sign.loc[prob_for_1['prob'] >= threshold] = 1
        # trade next day
        sign = sign.shift(-1).dropna()
        sign.columns = ['signal']
        return sign

    def logistic_reg_rolling(self, all_data, rolling_period, threshold):
        '''
        use rolling window method

        :param all_data: concating data of features and objective
        :param rolling_period:length
        :param threshold:if probability > threshold, then signal = 1

        '''

        X, y = all_data.iloc[:, :-1], all_data.iloc[:, -1]
        prob_for_1 = pd.DataFrame(index = list(X.index)[rolling_period:], columns = ['prob'])
        for i in range(len(all_data) - rolling_period):
            trainX, trainy = X.iloc[i:i + rolling_period, :], y.iloc[i:i + rolling_period]
            testX, testy = X.iloc[[i + rolling_period], :], y.iloc[i + rolling_period]
            logi_reg = LogisticRegression(penalty = 'l2', tol = 0.0001, solver = 'liblinear', C = 1.0, max_iter = 100)
            clf = logi_reg.fit(trainX, trainy)
            prob_for_1.iloc[i, 0] = clf.predict_proba(testX)[0, -1]
        sign = prob_for_1.copy()
        sign['prob'] = 0
        sign.loc[prob_for_1['prob'] >= threshold] = 1
        sign.columns = ['signal']
        # trade next day
        sign = sign.shift(-1).dropna()
        return sign

    def logistic_reg_expanding(self, all_data, starting_period, threshold):
        '''
        use expanding window method

        :param all_data: concating data of features and objective
        :param starting_period: statring length of window
        :param threshold: if probability > threshold, then signal = 1

        '''

        X, y = all_data.iloc[:, :-1], all_data.iloc[:, -1]
        prob_for_1 = pd.DataFrame(index = list(X.index)[starting_period:], columns = ['prob'])
        for i in range(len(all_data) - starting_period):
            trainX, trainy = X.iloc[:i + starting_period, :], y.iloc[:i + starting_period]
            testX, testy = X.iloc[[i + starting_period], :], y.iloc[i + starting_period]
            logi_reg = LogisticRegression(penalty = 'l2', tol = 0.0001, solver = 'liblinear', C = 1.0, max_iter = 100)
            clf = logi_reg.fit(trainX, trainy)
            prob_for_1.iloc[i, 0] = clf.predict_proba(testX)[0, -1]
        sign = prob_for_1.copy()
        sign['prob'] = 0
        sign.loc[prob_for_1['prob'] >= threshold] = 1
        sign.columns = ['signal']
        # trade next day
        sign = sign.shift(-1).dropna()

        return sign
