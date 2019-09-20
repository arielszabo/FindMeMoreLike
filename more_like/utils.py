import requests
from bs4 import BeautifulSoup
import re
import os
import json
import pandas as pd
from sklearn import metrics
from tqdm import tqdm
import logging

def open_json(full_file_path):
    with open(full_file_path, 'r') as jfile:
        return json.load(jfile)

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


def calculate_similarity(vectors_df, project_config):
    """
    calculate the similarity for the vectors.
    Save for each movie id a dict with the other movie id's as the keys and their similarity as values.


    :param vectors_df: [pandas' DataFrame] index must be the movies' id
    :param project_config: [dict] the project configuration
    """
    if project_config['similarity_method'] == 'cosine':
        similarity = metrics.pairwise.cosine_similarity(vectors_df)

    else:
        raise NotImplementedError("There is only an implementation for the cosine similarity for now")

    similarity_df = pd.DataFrame(similarity, index=vectors_df.index, columns=vectors_df.index)

    return similarity_df


def save_similarity_measures(similarity_df, project_config):
    """
    iterate over each line in the similarity DataFrame and save it to a json.
    Which looks like this:
    A list where each element is a dict of movie id and it's similarity value to the index movie id.
    The list is sorted from the highest similarity_value to the lowest
    [{'imdbID': , 'similarity_value':}, ...]


    :param similarity_df: [pandas' DataFrame]
    :param project_config: [dict] the project configuration
    """
    os.makedirs(project_config['similar_list_saving_path'], exist_ok=True)
    for idx, row in tqdm(similarity_df.iterrows(),
                         desc='Saving similarity measures',
                         leave=False):
        file_name = os.path.join(project_config['similar_list_saving_path'], '{}.json'.format(idx))
        # todo: save here the top K (form config) to save time in sorting later?
        row.sort_values(ascending=False).reset_index(name='similarity_value').to_json(file_name, orient='records')
