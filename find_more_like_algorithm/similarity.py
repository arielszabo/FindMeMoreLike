import asyncio
import json
import pathlib

import aiofiles
import gc
import numpy as np
import pandas as pd
from sklearn import metrics
from tqdm import tqdm

from find_more_like_algorithm import utils

from find_more_like_algorithm.constants import PROJECT_CONFIG, SAVING_MOVIES_LIMIT, root_path


def calculate(vectors_df, batch=False, save=False):
    """
    calculate the similarity for the vectors.
    Save for each movie id a dict with the other movie id's as the keys and their similarity as values.


    :param vectors_df: [pandas' DataFrame] index must be the movies' id
    :param batch:
    :param save:

    """
    if batch:
        all_batch_similarity_dfs = []
        for batch_similarity_df in batch_cosine_similarity(vectors_df):
            if save:
                save_similarity_measures(batch_similarity_df)
            else:
                all_batch_similarity_dfs.append(batch_similarity_df)
            gc.collect()

        similarity_df = pd.concat(all_batch_similarity_dfs)
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
    async def save_async(idx, row):
        prefix = utils.get_imdb_id_prefix_folder_name(idx)  # TODO chang this
        pathlib.Path(PROJECT_CONFIG['similar_list_saving_path'], prefix).mkdir(parents=True, exist_ok=True)
        file_name = pathlib.Path(PROJECT_CONFIG['similar_list_saving_path'], prefix, f'{idx}.json')
        row_data = row.sort_values(ascending=False).reset_index(name='similarity_value')
        top_row_data = list(row_data.itertuples(index=False, name=None))
        if SAVING_MOVIES_LIMIT is not None:
            top_row_data = top_row_data[:SAVING_MOVIES_LIMIT]

        json_dumped_data = json.dumps(top_row_data)

        async with aiofiles.open(file_name, 'w') as json_file:
            await json_file.write(json_dumped_data)

    pathlib.Path(root_path, PROJECT_CONFIG['similar_list_saving_path']).mkdir(parents=True, exist_ok=True)
    # for idx, row in tqdm(similarity_df.iterrows(),
    #                      desc='Saving similarity measures',
    #                      leave=False):
    #     prefix = get_imdb_id_prefix_folder_name(idx)
    #     os.makedirs(os.path.join(PROJECT_CONFIG['similar_list_saving_path'], prefix), exist_ok=True)
    #     file_name = os.path.join(PROJECT_CONFIG['similar_list_saving_path'], prefix, f'{idx}.json')
    #     row_data = row.sort_values(ascending=False).reset_index(name='similarity_value') # .to_json(file_name, orient='records')
    #     with open(file_name, "w") as json_file:
    #         json.dump(list(row_data.itertuples(index=False, name=None)), json_file)

    loop = asyncio.get_event_loop()
    list_of_saving_requests = [save_async(idx, row) for idx, row in tqdm(similarity_df.iterrows())]
    loop.run_until_complete(asyncio.gather(*list_of_saving_requests))


def batch_cosine_similarity(vectors_df):
    for vectors_df_batch_idxs in tqdm(utils.generate_list_chunks(vectors_df.index.tolist(), chunk_size=1_000)):
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