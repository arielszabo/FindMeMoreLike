import yaml
import logging
import os
import json
import datetime
from gensim.models import Doc2Vec
from tqdm import tqdm

from more_like import extraction, vectorization, utils


def get_the_data(project_config):  # todo: put this in a seperate file and import like this 'more_like.get_the_data'
    imdb_extractor = extraction.IMDBApiExtractor(project_config=project_config,
                                                 saving_path=project_config['api_data_saving_path']['imdb'])

    wiki_extractor = extraction.WikiApiExtractor(imdb_api_saving_path=project_config['api_data_saving_path']['imdb'],
                                                 project_config=project_config,
                                                 saving_path=project_config['api_data_saving_path']['wiki'])

    ids_to_query = utils.get_ids_from_web_page('https://www.imdb.com/scary-good/?ref_=nv_sf_sca')



    imdb_extractor.extract_data(ids_to_query=ids_to_query)
    wiki_extractor.extract_data(ids_to_query=ids_to_query)

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
    get_the_data(project_config)

    # CREATE The Vectors
    vectors_df = vectorization.create_vectors(project_config)
    # vectors_df.to_pickle('vectors_df_{}.pickle'.format(datetime.datetime.now().strftime('%d_%m_%Y')))

    # CALCULATE similarity
    similarity_df = utils.calculate_similarity(vectors_df, project_config)

    utils.save_similarity_measures(similarity_df, project_config=project_config)
