import os
import csv
import pandas as pd
import numpy as np
from options import base_dir, anchors, versions
from typing import List

anchors = pd.read_csv(f'{base_dir}{anchors}', header=None)


def read_data_from_csv() -> List | None:
    """
    loads the data from the csv file and returns a dictonary
    """
    try:
        codes = []

        for version in versions:
            filepath = f'{base_dir}{version}.csv'

            if not os.path.exists(filepath):
                raise FileNotFoundError(f'couldn\'t find {filepath}.')

            with open(filepath, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    code, code_description, anchor = row[0], row[1], row[3]
                    codes.append((versions.index(version), code,
                                 code_description, anchor))
        return codes

    except FileNotFoundError as e:
        print(e)

    return None


def read_data_from_csv_for(version) -> List | None:
    """
    loads the data from the csv file and returns a dictonary
    """
    try:
        codes = []
        filepath = f'{base_dir}{version}.csv'

        if not os.path.exists(filepath):
            raise FileNotFoundError(f'couldn\'t find {filepath}.')

        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                code, code_description, anchor = row[0], row[1], row[3]
                codes.append((version, code, code_description, anchor))
        return codes

    except FileNotFoundError as e:
        print(e)

    return None


def get_num_anchors() -> int:
    return len(anchors)


def get_anchors() -> List:
    return anchors.iloc[:, 1].tolist()


def get_one_hot_encoding(anchor: str) -> np.ndarray:
    anchor_list = get_anchors()
    if anchor not in anchor_list:
        print(anchor)
    vec = np.zeros(get_num_anchors())
    idx = anchor_list.index(anchor)
    vec[idx] = 1
    return vec


def get_max_num_codes() -> int:
    n_codes = list(map(lambda x: len(read_data_from_csv_for(
        x)) if read_data_from_csv_for(x) else 0, versions))

    return max(n_codes)
