import pathlib
from collections import Counter
from datetime import datetime
import pandas as pd
from tqdm import tqdm
from find_more_like_algorithm import utils
from find_more_like_algorithm.constants import WIKI_TEXT, FULL_TEXT, IMDB_ID, PLOT
from find_more_like_algorithm.utils import RAW_IMDB_DATA_PATH, RAW_WIKI_DATA_PATH


def load_saved_data():
    all_data = []

    imdb_data_dir_list = list(RAW_IMDB_DATA_PATH.glob(f"*/tt*.json"))
    # imdb_data_dir_list = imdb_data_dir_list[:100_000]

    for full_imdb_file_path in tqdm(imdb_data_dir_list, desc='Loading saved data ...'):
        imdb_data = utils.open_json(full_imdb_file_path)
        if imdb_data[PLOT].lower().strip() == "n/a":  # filter out movies with empty plots
            continue

        imdb_id = full_imdb_file_path.stem
        folder_prefix = utils.get_imdb_id_prefix_folder_name(imdb_id)
        full_wiki_file_path = RAW_WIKI_DATA_PATH.joinpath(folder_prefix, f"{imdb_id}.json")
        if full_wiki_file_path.exists():
            wiki_data = utils.open_json(full_wiki_file_path)

            imdb_data.update(wiki_data)

        all_data.append(imdb_data)

    df = pd.DataFrame(all_data)
    df = standardized(df)

    return df


def standardized(df):
    df.drop_duplicates(subset=[IMDB_ID], keep="first", inplace=True)  # TODO: find out why is there any at all: # tt9214844 tt5311542 tt10550884
    df.set_index(IMDB_ID, inplace=True)
    df[WIKI_TEXT] = df[WIKI_TEXT].fillna('')
    df[FULL_TEXT] = df[[PLOT, WIKI_TEXT]].apply(lambda plot_and_wiki_text: ' '.join(plot_and_wiki_text), axis=1)

    return df
