import os
from tqdm import tqdm
import logging
import pandas as pd
import importlib
from .. import utils


def load_data(project_config):
    all_data = []

    imdb_data_path = project_config['api_data_saving_path']['imdb']
    wiki_data_path = project_config['api_data_saving_path']['wiki']
    for file_name in tqdm(os.listdir(imdb_data_path), desc='Loading saved data ...'):
        imdb_data = utils.open_json(os.path.join(imdb_data_path, file_name))
        if file_name in os.listdir(wiki_data_path):
            wiki_data = utils.open_json(os.path.join(wiki_data_path, file_name))

            imdb_data.update(wiki_data)

        else:
            logging.info('{} has no wiki data'.format(file_name))
        all_data.append(imdb_data)

    return pd.DataFrame(all_data)  # todo: clean this DataFrame, do a 'total text' column etc

def create_vectors(project_config):
    df = load_data(project_config)

    all_vectors = []
    for vectorization_method in project_config['vectorization']:
        vectorization_module = importlib.import_module('.{}'.format(vectorization_method),
                                                       package='more_like.vectorization')
        vectors = getattr(vectorization_module, 'get_{}'.format(vectorization_method))(df, project_config)
        all_vectors.append(vectors)

    return pd.concat(all_vectors, axis=1, sort=False)  # todo: save them
