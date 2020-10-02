import pandas as pd
from datetime import datetime
import numpy as np
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
now = datetime.now()
dt_string = now.strftime('-%d-%m-%Y--%H:%M:%S')


def read_df(file_path):
    file_name = ''.join(file_path.split('.')[:-1])
    file_format_ = file_path.split('.')[-1]
    print('Analyzing Dict File: %s ...' % file_name)
    if file_format_ == 'txt':
        df = pd.read_csv(file_path, header=None)
        df.dropna(inplace=True)
        df = df.iloc[:, 0].str.strip().str.split(" ", n=1, expand=True)
    elif file_format_ == 'csv':
        df = pd.read_csv(file_path, header=None, usecols=[0, 1])
        df.dropna(inplace=True)
        df.iloc[:, 0] = df.iloc[:, 0].str.strip()
        df.iloc[:, 1] = df.iloc[:, 1].str.strip()
    else:
        print('Invalid File Format')
        print('----------------')
        return None
    df.reset_index(inplace=True, drop=True)
    df.sort_values(by=0, inplace=True, ignore_index=True)
    df_unique_row = df.drop_duplicates(ignore_index=True)
    if df.shape[0] != df_unique_row.shape[0]:
        print('%d Redundancy Case(s) Found and Removed' % (df.shape[0] - df_unique_row.shape[0]))
    ind_duplicated = df_unique_row.duplicated(subset=0, keep='first')
    if ind_duplicated.any():
        df_confused = df_unique_row.mask(~ind_duplicated)
        df_confused.dropna(inplace=True)
        print('%d Confusion Case(s) Found:' % df_confused.shape[0])
        print(df_confused.iloc[:, 0])
        print('----------------')
        return None
    print('Total: %d Words' % df_unique_row.shape[0])
    print('----------------')
    return df_unique_row


def write_to_csv(pd_series, prefix):
    if pd_series.shape[0] != 0:
        pd_series.sort_values(inplace=True, ignore_index=True)
        pd_series.to_csv(prefix + dt_string + '.csv', index=False, header=False, encoding='utf-8-sig')


if __name__ == '__main__':
    dict_current = read_df(sys.argv[1])
    if dict_current is not None:
        if len(sys.argv) == 2:
            file_format = sys.argv[1].split('.')[-1]
            # write to csv
            # csv_name = sys.argv[1].replace('.' + file_format, ''.join(['_checked' + dt_string + '.csv']))
            # dict_current.to_csv(csv_name, index=False, header=False, encoding='utf-8-sig')
            # write to txt
            txt_name = sys.argv[1].replace('.' + file_format, ''.join(['_checked' + dt_string + '.txt']))
            np.savetxt(txt_name, dict_current.values, fmt='%s', delimiter=' ')
        elif len(sys.argv) == 3:
            dict_compare = read_df(sys.argv[2])
            if dict_compare is not None:
                file_format = sys.argv[2].split('.')[-1]
                txt_name = sys.argv[2].replace('.' + file_format, ''.join(['_checked' + dt_string + '.txt']))
                np.savetxt(txt_name, dict_compare.values, fmt='%s', delimiter=' ')
                print('Comparing Two Dict Files ...')
                stack = [dict_current, dict_compare]
                # stack dict by removing duplicates- confusion case included (one word with multiple phonemes)
                dict_combined_subset0 = pd.concat(stack).drop_duplicates(subset=0, keep=False, ignore_index=True)
                s_current = dict_current.iloc[:, 0]
                s_compare = dict_compare.iloc[:, 0]
                s_combined_subset0 = dict_combined_subset0.iloc[:, 0]
                # newly-added words
                s_added = pd.Series(list(set(s_combined_subset0) & set(s_compare)))
                # words to be dropped in the latest dict
                s_dropped = pd.Series(list(set(s_combined_subset0) & set(s_current)))
                # words from the old dict (consist of modified and unchanged phonemes)
                s_maintained = pd.Series(list(set(s_current) & set(s_compare)))

                # stack dict by removing duplicates- only unchanged case included
                dict_combined = pd.concat(stack).drop_duplicates(keep=False, ignore_index=True)
                s_combined = dict_combined.iloc[:, 0]
                # modified words
                s_modified = pd.Series(list((set(s_combined.unique()) - set(s_added)) & set(s_compare)))
                # unchanged words
                s_no_change = pd.Series(list(set(s_maintained) - set(s_modified)))

                # summary
                print('%d Words Maintained:' % s_maintained.shape[0])
                print('  %d Words Modified' % s_modified.shape[0])
                print('  %d Words Unchanged' % s_no_change.shape[0])
                print('%d Words Added' % s_added.shape[0])
                print('%d Words Dropped' % s_dropped.shape[0])
                print('----------------')

                # write to csv
                write_to_csv(s_modified, 'modified')
                write_to_csv(s_no_change, 'unchanged')
                write_to_csv(s_added, 'added')
                write_to_csv(s_dropped, 'dropped')

            else:
                print('Encountered problem at file: %s' % sys.argv[2])
        else:
            print('Invalid argument(s)')
    else:
        print('Encountered problem at file: %s' % sys.argv[1])
