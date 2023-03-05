import efinance as ef
import pandas as pd


# use efinance to get data

class Get_data:

    def __init__(self, path = r'./', begin_date = '19000101', end_date = '20500101'):
        '''

        :param begin_date: str, the starting date of the data. eg:'19000101' represents 1900-01-01
        :param end_date: str, the ending date of the data
        :param path: path to store the data
        '''

        self.path = path
        self.begin_date = begin_date
        self.end_date = end_date

    def get_stock_data_and_store(self, code_list):
        '''
        get stocks in the code list and store with English columns name in self.path one by one

        :params code_list: the list of trading codes of stocks
        '''

        # get all the data of the main contracts
        data_dict = ef.stock.get_quote_history(code_list, beg = self.begin_date, end = self.end_date)
        for key, df in data_dict.items():
            df.drop(labels = ['涨跌额'], inplace = True, axis = 1)
            df.columns = ["chi_name", 'code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                          'change_percentage', 'turnover']

            df.to_csv(self.path + key + ".csv", encoding = 'gbk')

    def get_index_data(self, index_code):
        '''

        :param index_code: the code of the index
        '''

        df = ef.stock.get_quote_history(index_code, beg = self.begin_date, end = self.end_date)
        df.drop(labels = ['涨跌额'], inplace = True, axis = 1)
        df.columns = ["chi_name", 'code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                      'change_percentage', 'turnover']

        return df
