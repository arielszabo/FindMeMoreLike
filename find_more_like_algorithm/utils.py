import asyncio
import gc
import aiofiles
import requests
from bs4 import BeautifulSoup
import re
import os
import json
import pandas as pd
from sklearn import metrics
from tqdm import tqdm
import yaml
import numpy as np
from find_more_like_algorithm.constants import PROJECT_CONFIG, SAVING_MOVIES_LIMIT


def open_json(full_file_path):
    try:
        with open(full_file_path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(str(e), full_file_path)
        raise e


def open_yaml(full_file_path):
    with open(full_file_path, 'r') as yaml_file:
        return yaml.load(yaml_file)


def get_ids_from_web_page(html_url):
    """
    Extract movie ids from the html, given an url.
    :param [str] html_url: an url from which to extract movies by their id
    :return: A set of unique movie ids.
    """
    page = requests.get(url=html_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    ids = set()
    for link in soup.find_all('a'):
        for idx in re.findall(r'tt\d+', str(link)):
            ids.add(idx)

    return ids


def calculate_similarity(vectors_df, batch=False, save=False):
    """
    calculate the similarity for the vectors.
    Save for each movie id a dict with the other movie id's as the keys and their similarity as values.


    :param vectors_df: [pandas' DataFrame] index must be the movies' id
    """
    if PROJECT_CONFIG['similarity_method'] == 'cosine':
        if batch:
            similarity = batch_cosine_similarity(vectors_df, save=save)
            if similarity is None: return  # TODO: rewrite this
        else:
            similarity = metrics.pairwise.cosine_similarity(vectors_df)

    else:
        raise NotImplementedError("There is only an implementation for the cosine similarity for now")

    similarity_df = build_similarity_df(similarity, index_list=vectors_df.index.tolist())
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
        prefix = get_imdb_id_prefix_folder_name(idx)
        os.makedirs(os.path.join(PROJECT_CONFIG['similar_list_saving_path'], prefix), exist_ok=True)
        file_name = os.path.join(PROJECT_CONFIG['similar_list_saving_path'], prefix, f'{idx}.json')
        row_data = row.sort_values(ascending=False).reset_index(name='similarity_value')
        top_row_data = row_data[:SAVING_MOVIES_LIMIT]

        json_dumped_data = json.dumps(row_data)

        async with aiofiles.open(file_name, 'w') as json_file:
            await json_file.write(json_dumped_data)


    os.makedirs(PROJECT_CONFIG['similar_list_saving_path'], exist_ok=True)
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
    list_of_requests = [save_async(idx, row) for idx, row in tqdm(similarity_df.iterrows())]
    loop.run_until_complete(asyncio.gather(*list_of_requests))


def generate_list_chunks(list_, chunk_size):
    i = 0
    while True:
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size
        list_part = list_[start_index : end_index]
        i += 1
        yield list_part
        if end_index >= len(list_):
            break


def get_imdb_id_prefix_folder_name(imdb_id):
    return imdb_id[:4]



def batch_cosine_similarity(vectors_df, save=False):
    all_batch_similarity_arrays = []
    for vectors_df_batch_idxs in tqdm(generate_list_chunks(vectors_df.index.tolist(), chunk_size=1_000)):
        vectors_df_batch = vectors_df.loc[vectors_df_batch_idxs]
        batch_similarity = metrics.pairwise.cosine_similarity(vectors_df_batch, vectors_df)
        if save:
            batch_similarity_df = build_similarity_df(batch_similarity,
                                                      index_list=vectors_df_batch_idxs,
                                                      columns_list=vectors_df.index.tolist())
            save_similarity_measures(batch_similarity_df)
            gc.collect()
        else:
            all_batch_similarity_arrays.append(batch_similarity)

    if all_batch_similarity_arrays:
        similarity_array = np.concatenate(all_batch_similarity_arrays)
        return similarity_array


def build_similarity_df(similarity_array, index_list, columns_list=None):
    if columns_list is None:
        columns_list = index_list
    similarity_df = pd.DataFrame(similarity_array, index=index_list, columns=columns_list)
    return similarity_df
