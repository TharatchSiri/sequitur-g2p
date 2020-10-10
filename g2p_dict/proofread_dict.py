import pandas as pd
from datetime import datetime
import numpy as np
import sys
import warnings
from tabulate import tabulate
from tqdm import tqdm

warnings.filterwarnings("ignore", category=DeprecationWarning)


class ProofReadDict:
    def __init__(self, file_path):
        now = datetime.now()
        self.dt_string = now.strftime('-%d-%m-%Y--%H:%M:%S')
        self.file_path = file_path
        self.file_format = file_path.split('.')[-1]
        self.phoneme_list = pd.read_csv('phoneme_list.txt', header=None).iloc[:, 0].tolist()
        self.save_flag = False
        self.dict_df = self.read_dict()

    def save_dict(self, dict_, save_format_='txt'):
        suffix = ''.join(['_checked' + self.dt_string + '.' + save_format_])
        file_name = self.file_path.replace('.' + self.file_format, suffix)
        if save_format_ == 'csv':
            dict_.to_csv(file_name, index=False, header=False, encoding='utf-8-sig')
        elif save_format_ == 'txt':
            np.savetxt(file_name, dict_.values, fmt='%s', delimiter=' ')
        else:
            print('Invalid File Format to be Saved')

    def read_dict(self):
        file_name = ''.join(self.file_path.split('.')[:-1])
        print('Analyzing Dict File: %s ...' % file_name)

        # read file
        if self.file_format == 'txt':
            df = pd.read_csv(self.file_path, header=None)
            df.dropna(inplace=True)
            df = df.iloc[:, 0].str.strip().str.split(" ", n=1, expand=True)
        elif self.file_format == 'csv':
            df = pd.read_csv(self.file_path, header=None, usecols=[0, 1])
            df.dropna(inplace=True)
            df.iloc[:, 0] = df.iloc[:, 0].str.strip()
            df.iloc[:, 1] = df.iloc[:, 1].str.strip()
        else:
            print('Invalid File Format')
            print('****************')
            return None
        df.reset_index(inplace=True, drop=True)
        df.sort_values(by=0, inplace=True, ignore_index=True)

        # remove duplicated rows
        df_unique_row = df.drop_duplicates(ignore_index=True)
        if df.shape[0] != df_unique_row.shape[0]:
            self.save_flag = True
            print('%d Redundancy Case(s) Found and Removed' % (df.shape[0] - df_unique_row.shape[0]))

        # check confusion error
        ind_duplicated = df_unique_row.duplicated(subset=0, keep='first')
        if ind_duplicated.any():
            df_confused = df_unique_row.mask(~ind_duplicated)
            df_confused.dropna(inplace=True)
            print('%d Confusion Case(s) Found:' % df_confused.shape[0])
            print(tabulate(df_confused))
            print('****************')
            self.save_flag = False
            return None

        # check invalid phoneme error
        ind_array = []
        word_array = []
        invalid_array = []
        for ind, phoneme in enumerate(tqdm(df_unique_row.iloc[:, 1])):
            check_phoneme = pd.Series(phoneme.split(' ')).isin(self.phoneme_list)
            if not check_phoneme.all():
                ind_array.append(ind)
                word_array.append(df_unique_row.iloc[ind, 0])
                check_phoneme.where(check_phoneme == False, inplace=True)
                check_phoneme.dropna(inplace=True)
                wrong_spot = []
                for index in check_phoneme.index:
                    wrong_spot.append(phoneme.split(' ')[index])
                invalid_array.append(' '.join(wrong_spot))
        if len(ind_array) > 0:
            df_invalid = pd.DataFrame(np.transpose(np.array([word_array, invalid_array])))
            df_invalid.index = ind_array
            print('%d Invalid Symbol Case(s) Found:' % df_invalid.shape[0])
            print(tabulate(df_invalid))
            print('****************')
            self.save_flag = False
            return None

        # dict summary
        print('Total: %d Words' % df_unique_row.shape[0])
        print('****************')
        return df_unique_row


if __name__ == '__main__':
    res = ProofReadDict(file_path=sys.argv[1])
    if res.save_flag is True:
        res.save_dict(res.dict_df, save_format_='txt')
