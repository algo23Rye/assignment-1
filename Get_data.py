import efinance as ef
import pandas as pd


# use efinance to get index data

class Get_data:
    def __init__(self, code_list, path = r'./'):
        self.code_list = code_list
        self.path = path

    def get_stock_data_and_store(self):
        '''
        get stocks in the code list and store with English columns name in self.path one by one
        '''

        # get all the data of the main contracts
        data_dict = ef.stock.get_quote_history(self.code_list)
        for key, df in data_dict.items():
            df.drop(labels = ['涨跌额'], inplace = True, axis = 1)
            df.columns = ["chi_name", 'code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                          'change_percentage', 'turnover']

            df.to_csv(self.path + key + ".csv", encoding = 'gbk')
