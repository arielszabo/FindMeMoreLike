import yaml
import logging
import os

from more_like import extraction

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

    logging.info("Create folders to save raw data:")
    for api, saving_path in project_config['api_data_saving_path'].items():
        logging.info("raw data from the '{}' api is saved here - {}".format(api, saving_path))
        os.makedirs(saving_path, exist_ok=True)

    imdb_extractor = extraction.IMDBApiExtractor(project_config=project_config,
                                                 saving_path=project_config['api_data_saving_path']['imdb'])

    wiki_extractor = extraction.WikiApiExtractor(imdb_api_saving_path=project_config['api_data_saving_path']['imdb'],
                                                 project_config=project_config,
                                                 saving_path=project_config['api_data_saving_path']['wiki'])

    ids_to_query = extraction.get_ids_from_web_page('https://www.imdb.com/?ref_=nv_home')


    imdb_extractor.extract_data(ids_to_query=ids_to_query)
    wiki_extractor.extract_data(ids_to_query=ids_to_query)