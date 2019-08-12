import os
import re
import json
import glob
import requests
import time
import logging

class DataExtractor(object):
    def __init__(self, project_config, saving_path):
        self.project_config = project_config
        self.saving_path = saving_path
        self.existing_ids = self._get_existing_ids()

    def _get_existing_ids(self): #todo: maybe it's not a good idea ?
        all_saved_files = glob.glob(os.path.join(self.saving_path, '*.json'))
        return list(map(lambda name: re.search(r'tt\d+', name).group(0), all_saved_files))

    def extract_data(self, ids_to_query):
        pass  # This method needs to be implemented todo: add an assertion if not with the class name

    def save(self, data, movie_id):
        with open(os.path.join(self.saving_path, '{}.json'.format(movie_id)), 'w') as j_file:
            json.dump(data, j_file)


class IMDBApiExtractor(DataExtractor):
    def _get_user_api_key(self):
        with open(self.project_config['user_api_key_path']) as f:
            user_api_key = f.read()
        return user_api_key

    @staticmethod
    def _extract_a_single_id(movie_id, user_api_key):
        response = requests.get('http://www.omdbapi.com/?i={}&apikey={}&?plot=full'.format(movie_id,
                                                                                           user_api_key))

        if response.json() == {"Error": "Request limit reached!", "Response": "False"}:
            logging.info("Request limit reached! Lets wait 24 hours")
            time.sleep(86500)
            response = requests.get('http://www.omdbapi.com/?i={}&apikey={}&?plot=full'.format(movie_id,
                                                                                               user_api_key))
            # raise TypeError("Request limit reached!")

        if response.json()['Response'] == 'False':
            logging.info("Response == False ? at {}".format(movie_id))
            return None
            # raise ValueError("Response == False ? at {}".format(movie_id))

        return response

    def extract_data(self, ids_to_query):
        """
        Query and save movie data. Alert and raise errors if we reach the request limit or if the 'Response' is false.
        :param [list] ids_to_query: A list of movie ids to query the IMDB API
        :return: None, save the data json files
        """
        user_api_key = self._get_user_api_key()  # todo: is this a good way of doing this?

        logging.info('Extract {} movies data: {}'.format(len(ids_to_query), ids_to_query))

        for i, movie_id in enumerate(ids_to_query):
            if movie_id not in self.existing_ids: # if it's already existing then don't query it # todo: add a better cache invalidation
                response_data = self._extract_a_single_id(movie_id, user_api_key)
                if response_data:  # if it's not None
                    self.save(data=response_data, movie_id=movie_id)

            percent_queried = 100 * (i + 1) / len(ids_to_query)
            logging.info('Finished: {}%'.format(round(percent_queried, 2)))


