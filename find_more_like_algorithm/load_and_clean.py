from tqdm import tqdm
import pandas as pd
from datetime import datetime
import os
import logging
from find_more_like_algorithm import utils
from find_more_like_algorithm.constants import WIKI_TEXT, FULL_TEXT, IMDB_ID, INSERTION_TIME


def load_saved_data(project_config):
    all_data = []

    imdb_data_path = project_config['api_data_saving_path']['imdb']
    wiki_data_path = project_config['api_data_saving_path']['wiki']

    for file_name in tqdm(os.listdir(imdb_data_path), desc='Loading saved data ...'):
        full_file_path = os.path.join(imdb_data_path, file_name)
        imdb_data = utils.open_json(full_file_path)
        imdb_data[INSERTION_TIME] = datetime.fromtimestamp(os.path.getmtime(full_file_path))

        if file_name in os.listdir(wiki_data_path):
            wiki_data = utils.open_json(os.path.join(wiki_data_path, file_name))

            imdb_data.update(wiki_data)

        else:
            logging.warning('{} has no wiki data'.format(file_name))
        all_data.append(imdb_data)

    df = pd.DataFrame(all_data)
    df = standardized(df)

    return df


def standardized(df):
    df.set_index(IMDB_ID, inplace=True)
    df.columns = [col.lower() for col in df.columns]
    df[WIKI_TEXT] = df[WIKI_TEXT].fillna('')
    df[FULL_TEXT] = df.apply(lambda row: row['plot'] + ' ' + row[WIKI_TEXT], axis=1)

    return df
