import json
import logging
import math
import multiprocessing
import pathlib
import gc

import os
import pandas as pd
from sklearn import metrics
from tqdm import tqdm

from find_more_like_algorithm import utils

from find_more_like_algorithm.constants import SAVING_MOVIES_LIMIT
from find_more_like_algorithm.utils import PROJECT_CONFIG, SIMILAR_LIST_SAVING_PATH, NUMBER_OF_CONCURRENT_PROCESS

CALCULATE_CHUNKS_AMOUNT = 1_000


def calculate(vectors_df, use_multiprocessing=False):
    """
    calculate the similarity for the vectors.
    Save for each movie id a dict with the other movie id's as the keys and their similarity as values.


    :param vectors_df: [pandas' DataFrame] index must be the movies' id
    :param batch:
    :param save:
    :param use_multiprocessing:

    """
    for batch_similarity_df in get_cosine_similarity_batches(vectors_df, use_multiprocessing):
        save_similarity_measures(batch_similarity_df)
        gc.collect()


def save_similarity_measures(similarity_df):
    """
    iterate over each line in the similarity DataFrame and save it to a json.
    Which looks like this:
    A list where each element is a dict of movie id and it's similarity value to the index movie id.
    The list is sorted from the highest similarity_value to the lowest
    [{'imdbID': , 'similarity_value':}, ...]


    :param similarity_df: [pandas' DataFrame]
    """
    for imdb_id, similarity_row in tqdm(similarity_df.iterrows(),
                                        desc="save similarity measures",
                                        total=similarity_df.shape[0]):
    # for imdb_id, similarity_row in similarity_df.iterrows():
        _save_single_similarity_row(imdb_id, similarity_row)


def _save_single_similarity_row(imdb_id, row):
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


def get_vectors_df_and_vectors_df_batch(vectors_df):
    for vectors_df_batch_indexs in utils.generate_list_chunks(vectors_df.index.tolist(),
                                                              chunks_amount=CALCULATE_CHUNKS_AMOUNT):
        vectors_df_batch = vectors_df.loc[vectors_df_batch_indexs]
        yield (vectors_df, vectors_df_batch)


def get_cosine_similarity_batches(vectors_df, use_multiprocessing=False):
    # TODO make this more readable:
    if use_multiprocessing:
        chunk_size = NUMBER_OF_CONCURRENT_PROCESS * 2
        list_of_batch_arguments = utils.generate_list_chunks(get_vectors_df_and_vectors_df_batch(vectors_df),
                                                             chunk_size=chunk_size)
        for batch_cosine_similarity_arguments in tqdm(list(list_of_batch_arguments),
                                                      desc="calculating batch cosine similarity with multiprocessing"):
            with multiprocessing.Pool(chunk_size) as pool:
                list_of_batch_similarity_df = pool.starmap(_batch_cosine_similarity, batch_cosine_similarity_arguments)

            for batch_similarity_df in list_of_batch_similarity_df:
                yield batch_similarity_df

    else:
        for vectors_df, vectors_df_batch in tqdm(get_vectors_df_and_vectors_df_batch(vectors_df),
                                                 desc="calculating batch cosine similarity",
                                                 total=CALCULATE_CHUNKS_AMOUNT):
            batch_similarity_df = _batch_cosine_similarity(vectors_df, vectors_df_batch)
            yield batch_similarity_df


def _batch_cosine_similarity(vectors_df, vectors_df_batch):
    batch_similarity_array = metrics.pairwise.cosine_similarity(vectors_df_batch, vectors_df)
    batch_similarity_df = build_similarity_df_from_array(batch_similarity_array,
                                                         index_list=vectors_df_batch.index.tolist(),
                                                         columns_list=vectors_df.index.tolist())
    return batch_similarity_df


def build_similarity_df_from_array(similarity_array, index_list, columns_list=None):
    if columns_list is None:
        columns_list = index_list
    similarity_df = pd.DataFrame(similarity_array, index=index_list, columns=columns_list)
    return similarity_df
