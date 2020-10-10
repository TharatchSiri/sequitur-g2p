import pandas as pd
from datetime import datetime
import sys
import warnings
from proofread_dict import ProofReadDict

warnings.filterwarnings("ignore", category=DeprecationWarning)
now = datetime.now()
dt_string = now.strftime('-%d-%m-%Y--%H:%M:%S')


def save_list(series_, name_='unspecified'):
    if series_.shape[0] != 0:
        series_.sort_values(inplace=True, ignore_index=True)
        series_.to_csv(name_ + dt_string + '.csv', index=False, header=False, encoding='utf-8-sig')


if __name__ == '__main__':
    # load dicts
    res_current = ProofReadDict(file_path=sys.argv[1])
    res_compare = ProofReadDict(file_path=sys.argv[2])

    # dict comparison
    if (res_current.dict_df is not None) & (res_compare.dict_df is not None):
        print('Comparing Two Dict Files ...')
        stack = [res_current.dict_df, res_compare.dict_df]
        # stack dict by removing duplicates- confusion case included (one word with multiple phonemes)
        dict_combined_subset0 = pd.concat(stack).drop_duplicates(subset=0, keep=False, ignore_index=True)
        s_current = res_current.dict_df.iloc[:, 0]
        s_compare = res_compare.dict_df.iloc[:, 0]
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
        save_list(s_modified, 'modified')
        save_list(s_no_change, 'unchanged')
        save_list(s_added, 'added')
        save_list(s_dropped, 'dropped')
