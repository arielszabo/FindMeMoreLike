import yaml
import logging
import os
import json
from gensim.models import Doc2Vec
from tqdm import tqdm

from more_like import extraction, vectorization, utils


def open_json(full_file_path):
    with open(full_file_path, 'r') as jfile:
        x = json.load(jfile)
    return x


def get_the_vectors(project_config): # todo: REFACTOR this is not the way this should be
    doc2vec = Doc2Vec.load(project_config['doc2vec_model_path'])

    os.makedirs(project_config['vectors_saving_path'], exist_ok=True)

    imdb_data_path = project_config['api_data_saving_path']['imdb']
    wiki_data_path = project_config['api_data_saving_path']['wiki']
    for file_name in tqdm(os.listdir(imdb_data_path)):
        imdb_data = open_json(os.path.join(imdb_data_path, file_name))
        if file_name in os.listdir(wiki_data_path):
            wiki_data = open_json(os.path.join(wiki_data_path, file_name))
            imdb_data['Plot'] += ' ' + wiki_data['text']

        else:
            logging.info('{} has no wiki data'.format(file_name))

        vec = vectorization.get_text_vectors(txt=imdb_data['Plot'], doc2vec_model=doc2vec)

        with open(os.path.join(project_config['vectors_saving_path'], file_name), 'w') as jfile:
            json.dump(vec, jfile)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
            logging.StreamHandler()
        ])


    with open('project_config.yaml', 'r') as yfile:
        project_config = yaml.load(yfile)

    logging.info(project_config)

    # GET The data:
    logging.info("Create folders to save raw data:")
    for api, saving_path in project_config['api_data_saving_path'].items():
        logging.info("raw data from the '{}' api is saved here - {}".format(api, saving_path))
        os.makedirs(saving_path, exist_ok=True)

    imdb_extractor = extraction.IMDBApiExtractor(project_config=project_config,
                                                 saving_path=project_config['api_data_saving_path']['imdb'])

    wiki_extractor = extraction.WikiApiExtractor(imdb_api_saving_path=project_config['api_data_saving_path']['imdb'],
                                                 project_config=project_config,
                                                 saving_path=project_config['api_data_saving_path']['wiki'])

    ids_to_query = utils.get_ids_from_web_page('https://www.imdb.com/scary-good/?ref_=nv_sf_sca')



    imdb_extractor.extract_data(ids_to_query=ids_to_query)
    wiki_extractor.extract_data(ids_to_query=ids_to_query)


    # CREATE The Vectors
    get_the_vectors(project_config=project_config)


    # CONCAT The Vectors
    vectors_df = utils.concatenate_vectors(project_config)

    # CALCULATE similarity
    utils.calculate_similarity(vectors_df, project_config)