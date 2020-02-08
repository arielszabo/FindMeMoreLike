import json
import logging
import multiprocessing
import pathlib
import gc
import pandas as pd
from sklearn import metrics
from tqdm import tqdm

from find_more_like_algorithm import utils

from find_more_like_algorithm.constants import SAVING_MOVIES_LIMIT
from find_more_like_algorithm.utils import PROJECT_CONFIG, SIMILAR_LIST_SAVING_PATH


def calculate(vectors_df, batch=False, save=False, use_multiprocessing=False):
    """
    calculate the similarity for the vectors.
    Save for each movie id a dict with the other movie id's as the keys and their similarity as values.


    :param vectors_df: [pandas' DataFrame] index must be the movies' id
    :param batch:
    :param save:
    :param use_multiprocessing:

    """
    if batch and save:
        for batch_similarity_df in batch_cosine_similarity(vectors_df, use_multiprocessing):
            save_similarity_measures(batch_similarity_df)
            gc.collect()
        return

    if batch:
        all_batch_similarity_dfs = list(batch_cosine_similarity(vectors_df))
        similarity_df = pd.concat(all_batch_similarity_dfs)
        gc.collect()
    else:
        similarity_array = metrics.pairwise.cosine_similarity(vectors_df)
        similarity_df = build_similarity_df(similarity_array, index_list=vectors_df.index.tolist())

    if save:
        save_similarity_measures(similarity_df)
    else:
        return similarity_df


def save_similarity_measures(similarity_df):
    """
    iterate over each line in the similarity DataFrame and save it to a json.
    Which looks like this:
    A list where each element is a dict of movie id and it's similarity value to the index movie id.
    The list is sorted from the highest similarity_value to the lowest
    [{'imdbID': , 'similarity_value':}, ...]


    :param similarity_df: [pandas' DataFrame]
    """
    def save(imdb_id, row):
        prefix = utils.get_imdb_id_prefix_folder_name(imdb_id)
        file_path = SIMILAR_LIST_SAVING_PATH.joinpath(prefix, f'{imdb_id}.json')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        row_data = row.sort_values(ascending=False).reset_index(name='similarity_value')
        top_row_data = list(row_data.itertuples(index=False, name=None))
        if SAVING_MOVIES_LIMIT is not None:
            top_row_data = top_row_data[:SAVING_MOVIES_LIMIT]

        json_dumped_data = json.dumps(top_row_data)

        with file_path.open('w') as json_file:
            json_file.write(json_dumped_data)

    for imdb_id, similarity_row in tqdm(similarity_df.iterrows(),
                                        desc="save similarity measures",
                                        total=similarity_df.shape[0]):
        save(imdb_id, similarity_row)


def batch_cosine_similarity(vectors_df, use_multiprocessing=False):
    list_of_vectors_df_batch_indexs = utils.generate_list_chunks(vectors_df.index.tolist(), chunk_size=1_000)
    if use_multiprocessing:
        logging.info("use multiprocessing")
        list_of_batch_cosine_similarity_arguments = [(vectors_df, vectors_df_batch_idxs)
                                                     for vectors_df_batch_idxs in list_of_vectors_df_batch_indexs]
        logging.info("start calculating batch cosine similarity multiprocessing")
        with multiprocessing.Pool() as pool:
            results = pool.starmap(_batch_cosine_similarity, list_of_batch_cosine_similarity_arguments)
        return list(results)
    else:
        for vectors_df_batch_indexs in tqdm(list_of_vectors_df_batch_indexs):
            batch_similarity_df = _batch_cosine_similarity(vectors_df, vectors_df_batch_indexs)
            yield batch_similarity_df


def _batch_cosine_similarity(vectors_df, vectors_df_batch_idxs):
    vectors_df_batch = vectors_df.loc[vectors_df_batch_idxs]
    batch_similarity_array = metrics.pairwise.cosine_similarity(vectors_df_batch, vectors_df)
    batch_similarity_df = build_similarity_df(batch_similarity_array,
                                              index_list=vectors_df_batch_idxs,
                                              columns_list=vectors_df.index.tolist())
    yield batch_similarity_df


def build_similarity_df(similarity_array, index_list, columns_list=None):
    if columns_list is None:
        columns_list = index_list
    similarity_df = pd.DataFrame(similarity_array, index=index_list, columns=columns_list)
    return similarity_df
