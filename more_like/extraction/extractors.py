import os
import re
import json
import glob
import requests
import time
import logging
from bs4 import BeautifulSoup

class DataExtractor(object):
    def __init__(self, project_config, saving_path):
        self.project_config = project_config
        self.saving_path = saving_path # todo: maybe add an extractor type arg and eith that arg go to the relevant key in the config?
        self.existing_ids = self._get_existing_ids()

    def _get_existing_ids(self): #todo: maybe it's not a good idea ?
        all_saved_files = glob.glob(os.path.join(self.saving_path, '*.json'))
        return list(map(lambda name: re.search(r'tt\d+', name).group(0), all_saved_files))

    def _extract_a_single_id(self, movie_id): # This method needs to be implemented
        pass  # This method needs to be implemented todo: add an assertion if not with the class name

    def extract_data(self, ids_to_query):
        if not isinstance(ids_to_query, (tuple, list)):
            ids_to_query = [ids_to_query]
        for i, movie_id in enumerate(ids_to_query):
            if movie_id in self.existing_ids: # if it's already existing then don't query it # todo: add a better cache invalidation
                logging.info("{} already exists here - {}".format(movie_id, self.saving_path))
            else:
                single_movie_data = self._extract_a_single_id(movie_id) # This method needs to be implemented
                if single_movie_data:  # if it's not None
                    self.save(data=single_movie_data, movie_id=movie_id)

            percent_queried = 100 * (i + 1) / len(ids_to_query)
            logging.info('Finished: {}%'.format(round(percent_queried, 2)))

    def save(self, data, movie_id):
        with open(os.path.join(self.saving_path, '{}.json'.format(movie_id)), 'w') as j_file:
            json.dump(data, j_file)

class IMDBApiExtractor(DataExtractor):
    def __init__(self, *args, **kwargs): # todo: is this the best way?
        super().__init__(*args, **kwargs)
        self.user_api_key = self._get_user_api_key()

    def _get_user_api_key(self):
        with open(self.project_config['user_api_key_path']) as f:
            user_api_key = f.read()
        return user_api_key

    def _extract_a_single_id(self, movie_id):
        response = requests.get('http://www.omdbapi.com/?i={}&apikey={}&?plot=full'.format(movie_id,
                                                                                           self.user_api_key))

        if response.json() == {"Error": "Request limit reached!", "Response": "False"}:
            logging.info("Request limit reached! Lets wait 24 hours")
            time.sleep(86500)
            response = requests.get('http://www.omdbapi.com/?i={}&apikey={}&?plot=full'.format(movie_id,
                                                                                               self.user_api_key))
            # raise TypeError("Request limit reached!")

        if response.json()['Response'] == 'False':
            logging.info("Response == False ? at {}".format(movie_id))
            return None
            # raise ValueError("Response == False ? at {}".format(movie_id))

        return response.json()

class WikiApiExtractor(DataExtractor):
    def __init__(self, imdb_api_saving_path, *args, **kwargs): # todo: is this the best way?
        super().__init__(*args, **kwargs)
        self.imdb_api_saving_path = imdb_api_saving_path
        self.api_url = r'https://en.wikipedia.org/w/api.php'

    def _build_text_query(self, movie_id):
        file_name = os.path.join(self.imdb_api_saving_path, '{}.json'.format(movie_id))
        if os.path.exists(file_name):
            with open(file_name, 'r') as jfile:
                movie_json = json.load(jfile)
            query_info = [movie_json['Title'], movie_json['Year'], movie_json['Type'], movie_json['Director']]
            return ' '.join(query_info)

        else:
            logging.info("There is no IMDB data for this IMDB_id")
            return None

    def _get_page_id_by_text_search(self, text_to_search_for):
        if len(text_to_search_for) > 300: # WIKI Search request have a maximum allowed length of 300 chars
            text_to_search_for = text_to_search_for[:300]
        get_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': text_to_search_for
        }
        response = requests.get(url=self.api_url, params=get_params)

        if int(response.status_code) != 200:
            logging.info(f'The request for "{text_to_search_for}" returned with status_code: {response.status_code}')
            # todo: something better
            return None

        if response.json()['query']['searchinfo']['totalhits'] == 0:
            logging.info(f'"{text_to_search_for}" have no results')
            return None  # todo: something better

        if 'error' in response.json():
            logging.info(f'"{text_to_search_for}" had an error')
            return None  # todo: something better

        return response.json()["query"]["search"][0]["pageid"]  # the first one is the best match

    def _extract_text_first_section(self, page_id):
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'extracts',
            'exintro': 'True',
            'pageids': page_id
        }
        response = requests.get(url=self.api_url, params=params)

        if int(response.status_code) != 200:
            logging.info(f'The request for "{page_id}" returned with status_code: {response.status_code}') #todo: something better
            return None

        html_content = response.json()['query']['pages'][str(page_id)]['extract']
        return BeautifulSoup(html_content, 'html.parser').get_text()

    def _extract_a_single_id(self, movie_id):
        text_query = self._build_text_query(movie_id)
        if text_query:  # if it's not None
            wiki_page_id = self._get_page_id_by_text_search(text_query)
            if wiki_page_id:  # if it's not None
                text_content = self._extract_text_first_section(wiki_page_id)
                if text_content:  # if it's not None
                    wiki_data = {'text': text_content,
                                 'wiki_page_id': wiki_page_id,
                                 'imdb_id': movie_id}
                    return wiki_data # else will return None and the 'extract_data' method won't save it