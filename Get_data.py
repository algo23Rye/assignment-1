import efinance as ef
import pandas as pd


# use efinance to get index data

class Get_data:
    def __init__(self, path = r'./'):
        self.path = path

    def get_stock_data_and_store(self, code_list):
        '''
        get stocks in the code list and store with English columns name in self.path one by one

        :params code_list: the list of trading codes of stocks
        '''

        # get all the data of the main contracts
        data_dict = ef.stock.get_quote_history(code_list)
        for key, df in data_dict.items():
            df.drop(labels = ['涨跌额'], inplace = True, axis = 1)
            df.columns = ["chi_name", 'code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                          'change_percentage', 'turnover']

            df.to_csv(self.path + key + ".csv", encoding = 'gbk')

    def get_index_data(self, index_code):
        '''

        :param index_code: the code of the index
        '''
        df = ef.stock.get_quote_history(index_code)
        df.drop(labels = ['涨跌额'], inplace = True, axis = 1)
        df.columns = ["chi_name", 'code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                      'change_percentage', 'turnover']

        return df

