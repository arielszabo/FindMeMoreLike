import os
import re
import json
import glob
import requests
import time
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm

class DataExtractor(object):
    def __init__(self, project_config, saving_path):
        self.project_config = project_config
        self.saving_path = saving_path # todo: maybe add an extractor type arg and with that arg go to the relevant key in the config?
        os.makedirs(self.saving_path, exist_ok=True)
        self.existing_ids = self._get_existing_ids()

    def _get_existing_ids(self):
        all_saved_files = glob.glob(os.path.join(self.saving_path, '*.json'))
        return list(map(lambda name: re.search(r'tt\d+', name).group(0), all_saved_files))

    def _extract_a_single_id(self, movie_id):
        raise NotImplementedError("This method needs to be implemented here {}".format(type(self).__name__))

    def extract_data(self, ids_to_query):
        if not isinstance(ids_to_query, (tuple, list, set)):
            ids_to_query = [ids_to_query]
        for i, movie_id in tqdm(enumerate(ids_to_query), desc='Extracted'):
            if movie_id in self.existing_ids: # if it's already existing then don't query it # todo: add a better cache invalidation
                logging.info("{} already exists here - {}".format(movie_id, self.saving_path))
            else:
                single_movie_data = self._extract_a_single_id(movie_id) # This method needs to be implemented
                if single_movie_data:  # if it's not None
                    self.save(data=single_movie_data, movie_id=movie_id)

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
        self.rest_api_url = 'https://en.wikipedia.org/api/rest_v1'

    def _build_text_query(self, movie_id):
        file_name = os.path.join(self.imdb_api_saving_path, '{}.json'.format(movie_id))
        if os.path.exists(file_name):
            with open(file_name, 'r') as jfile:
                movie_json = json.load(jfile)
            query_info = [movie_json['Title'], movie_json['Year'], movie_json['Type']] # , movie_json['Director']
            return query_info

        else:
            logging.info("There is no IMDb data for this {} IMDb id".format(movie_id))
            return None

    def _get_page_id_by_text_search(self, query_properties):
        """

        :param query_properties: [list] a list of the movie properties to use to build the text query.
        :return:
        """
        # WIKI Search request have a maximum allowed length of 300 chars
        query_properties = self.adjust_to_maximum_allowed_query_length(query_properties, max_length=300)

        while query_properties:  # while the list is not empty
            text_to_search_for = ' '.join(query_properties)

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

            if 'error' in response.json():
                logging.info(f'"{text_to_search_for}" had an error')
                return None

            if response.json()['query']['searchinfo']['totalhits'] == 0:
                logging.info(f'"{text_to_search_for}" have no results')
                # reconstruct the query_properties with less info so maybe the query will succeed:
                query_properties = query_properties[:-1]
            else:
                best_match = response.json()["query"]["search"][0]  # the first one is the best match
                return best_match["pageid"], best_match["title"]

    @staticmethod
    def adjust_to_maximum_allowed_query_length(query_properties, max_length=300):
        """

        :param query_properties: [list] a list of the movie properties to use to build the text query.
        :param max_length: [int] the maximum size of characters wiki allows to send in a query.
        :return:
        """
        allowed_size_query_properties = []
        total_length = 0
        for i in query_properties:
            total_length += len(i) + 1  # the additional 1 is for the space between words
            if total_length <= max_length + 1: # the additional 1 is for the extra space after the last word
                allowed_size_query_properties.append(i)

        return allowed_size_query_properties

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
        soup = BeautifulSoup(html_content, 'html.parser').get_text()

        return '\n'.join([p.get_text() for p in soup.find_all('p')])

    def _extract_all_text(self, page_title):
        res = requests.get('{rest_api_path}/page/html/{title}?redirect=true'.format(rest_api_path=self.rest_api_url,
                                                                                    title=page_title.replace(' ', '_')
                                                                                    ))
        if int(res.status_code) != 200:
            logging.info(f'The request for "{page_title}" returned with status_code: {res.status_code}') #todo: something better
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        return '\n'.join([p.get_text() for p in soup.find_all('p')])

    # @staticmethod
    # def _movie_related_page_found(text):
    #     for word in ['movie', 'film', 'show', 'television']:
    #         if re.findall(r'[\s\b]?{}[\s\b]?'.format(word), text.lower()):  # if it not empty
    #             return True
    #     return False

    def _extract_a_single_id(self, movie_id):
        text_query = self._build_text_query(movie_id)
        if text_query:  # if it's not None
            wiki_page_id, wiki_page_title = self._get_page_id_by_text_search(text_query)
            # if wiki_page_id:  # if it's not None
            #     text_content = self._extract_text_first_section(wiki_page_id)
            if wiki_page_title:  # if it's not None
                text_content = self._extract_all_text(page_title=wiki_page_title)
                if text_content:  # if it's not None
                    wiki_data = {'text': text_content.lower(),
                                 'wiki_page_id': wiki_page_id,
                                 'imdb_id': movie_id}
                    return wiki_data # else will return None and the 'extract_data' method won't save it