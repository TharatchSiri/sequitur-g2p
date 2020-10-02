import argparse
import os
import numpy as np
from datetime import datetime

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='split train test')
    parser.add_argument("g2p_corpus", type=str, help='corpus file')
    args = parser.parse_args()

    g2p_corpus = args.g2p_corpus
    
    with open(g2p_corpus) as f:
        lines = f.readlines()
        np.random.shuffle(lines)
        
        n_train_sample = int(len(lines)*0.98)
        train_list = lines[:n_train_sample]
        test_list = lines[n_train_sample:]

        # create folder
        train_path = 'g2p_dict/training_data'
        if not os.path.exists(train_path):
            os.makedirs(train_path)

        # filename
        now = datetime.now()
        dt_string = now.strftime('%d-%m-%Y--%H-%M')
        folder_path = os.path.join(train_path, dt_string)
        os.makedirs(folder_path)

        with open(os.path.join(folder_path, 'train.txt'), 'w+') as train_f:
            for train_s in train_list:
                train_f.write(train_s)
        
        with open(os.path.join(folder_path, 'test.txt'), 'w+') as test_f:
            for test_s in test_list:
                test_f.write(test_s)
        
        print("Train sample : "+str(len(train_list)))
        print("Test sample : "+str(len(test_list)))

        # pip install -i https://test.pypi.org/simple/ sequitur-g2p
        # pip install six==1.11.0
