from tqdm import tqdm
import pandas as pd
from datetime import datetime
import logging
import pathlib
import glob
from find_more_like_algorithm import utils
from find_more_like_algorithm.constants import WIKI_TEXT, FULL_TEXT, IMDB_ID, INSERTION_TIME, PROJECT_CONFIG


def load_saved_data():
    all_data = []

    imdb_data_path = pathlib.Path(PROJECT_CONFIG['api_data_saving_path']['imdb'])
    imdb_data_dir_list = imdb_data_path.glob(f"*/tt*.json")
    imdb_data_dir_list = list(imdb_data_dir_list)

    wiki_data_path = PROJECT_CONFIG['api_data_saving_path']['wiki']

    for full_imdb_file_path in tqdm(imdb_data_dir_list, desc='Loading saved data ...'):
        imdb_data = utils.open_json(full_imdb_file_path)
        imdb_data[INSERTION_TIME] = datetime.fromtimestamp(full_imdb_file_path.stat().st_mtime)


        imdb_id = full_imdb_file_path.stem
        folder_prefix = utils.get_imdb_id_prefix_folder_name(imdb_id)
        full_wiki_file_path = pathlib.Path(wiki_data_path, folder_prefix, f"{imdb_id}.json")
        if full_wiki_file_path.exists():
            wiki_data = utils.open_json(full_wiki_file_path)

            imdb_data.update(wiki_data)

        # else:
        #     logging.warning('{} has no wiki data'.format(file_name))
        all_data.append(imdb_data)

    df = pd.DataFrame(all_data)
    df = standardized(df)

    return df


def standardized(df):
    df.set_index(IMDB_ID, inplace=True)
    df.columns = [col.lower() for col in df.columns]
    df[WIKI_TEXT] = df[WIKI_TEXT].fillna('')
    df[FULL_TEXT] = df[['plot', WIKI_TEXT]].apply(lambda plot_and_wiki_text: ' '.join(plot_and_wiki_text), axis=1)

    return df
