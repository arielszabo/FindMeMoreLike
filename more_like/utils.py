import requests
from bs4 import BeautifulSoup
import re
import os
import json
import pandas as pd
from sklearn import metrics

def get_ids_from_web_page(html_url):
    """
    Extract movie ids from the html, given an url.
    :param [str] html_url: an url from which to extract movies by their id
    :return: A set of unique movie ids.
    """
    page = requests.get(url=html_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    ids = []
    for link in soup.find_all('a'):
        for idx in re.findall(r'tt\d+', str(link)):
            ids.append(idx)

    return set(ids)


def concatenate_vectors(project_config):
    """
    Open all the json files which hold for each IMDb id the movie's vector, concatenate them to a pandas DataFrame.
    :param project_config: [dict] the project configuration
    :return: [pandas' DataFrame]
    """
    vectors_data = {}
    for vector_file_name in os.listdir(project_config['vectors_saving_path']):
        with open(os.path.join(project_config['vectors_saving_path'], vector_file_name), 'r') as json_file:
            vector = json.load(json_file)

        imdb_id = vector_file_name.split('.')[0] # to get only the part before the '.json' # todo: maybe do a regex?
        vectors_data[imdb_id] = vector

    return pd.DataFrame.from_dict(vectors_data, orient='index')


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

    save_similarity_measures(similarity_df, project_config=project_config)

    return similarity_df


def save_similarity_measures(similarity_df, project_config):
    """
    iterate over each line in the similarity DataFrame and save it to a json.

    :param similarity_df: [pandas' DataFrame]
    :param project_config: [dict] the project configuration
    """
    os.makedirs(project_config['similar_list_saving_path'], exist_ok=True)
    for idx, row in similarity_df.iterrows():
        file_name = os.path.join(project_config['similar_list_saving_path'], '{}.json'.format(idx))
        row.sort_values(ascending=False).to_json(file_name)