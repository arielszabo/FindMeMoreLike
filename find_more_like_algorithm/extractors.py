import os
import re
import json
import glob
import requests
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm
import yaml
import math
from find_more_like_algorithm.constants import WIKI_TEXT
from find_more_like_algorithm import utils
import asyncio
import aiofiles
import aiohttp

CHUNK_SIZE = 25

class ExceptedExtractorFail(Exception):
    pass


class DataExtractor(object):
    def __init__(self, project_config):
        self.project_config = project_config
        self.saving_path = self.project_config["api_data_saving_path"][self.extractor_type]
        os.makedirs(self.saving_path, exist_ok=True)
        self.existing_ids = self._get_existing_ids()

    def _get_existing_ids(self):
        all_saved_files = glob.glob(os.path.join(self.saving_path, '*.json'))
        return [re.search(r'tt\d+', name).group(0) for name in all_saved_files]

    def extract_data(self, ids_to_query):
        chunks_amount = math.ceil(len(ids_to_query) / CHUNK_SIZE)
        for ids_to_query_chunk in tqdm(utils.generate_list_chunks(ids_to_query, CHUNK_SIZE),
                                       desc=f"Extract ({self.extractor_type}) {len(ids_to_query)} items in chunks of {CHUNK_SIZE}",
                                       total=chunks_amount):
            loop = asyncio.get_event_loop()

            list_of_requests = []
            for movie_id in ids_to_query_chunk:
                if movie_id not in self.existing_ids:
                    list_of_requests.append(self._extract_and_save(movie_id))

            loop.run_until_complete(asyncio.gather(*list_of_requests))

    async def save(self, data, movie_id):
        async with aiofiles.open(os.path.join(self.saving_path, '{}.json'.format(movie_id)), 'w') as j_file:
            json.dump(data, j_file)

    async def _save_errors(self, error, movie_id):
        day_string = datetime.now().strftime("%Y-%m-%d")
        error_saving_folder_path = os.path.join(self.project_config["error_saving_path"], day_string)
        os.makedirs(error_saving_folder_path, exist_ok=True)

        full_error_saving_path = os.path.join(error_saving_folder_path, f"{movie_id}_{self.__class__.__name__}.txt")
        async with aiofiles.open(full_error_saving_path, 'w') as text_file:
            await text_file.write(str(error))

    async def _extract_and_save(self, movie_id):
        try:
            single_movie_data = await self._extract_a_single_id(movie_id)
            if single_movie_data is not None:
                await self.save(data=single_movie_data, movie_id=movie_id)
        except ExceptedExtractorFail:
            pass
        except Exception as error:
            await self._save_errors(error, movie_id)


class IMDBApiExtractor(DataExtractor):

    def __init__(self, *args, **kwargs): # todo: is this the best way?
        self.extractor_type = 'imdb'
        super().__init__(*args, **kwargs)
        self.user_api_key = self._get_user_api_key()


    def _get_user_api_key(self):
        if not os.path.exists(self.project_config['keys_config_path']):
            assert FileNotFoundError(f"Save you OMDb api key in the file {self.project_config['keys_config_path']}."
                                     f" Please read the README file for more info")
        with open(self.project_config['keys_config_path'], 'r') as f:
            user_api_key = yaml.load(f)["omdb_user_key"]
        return user_api_key

    async def _extract_a_single_id(self, movie_id):
        url = f'https://omdbapi.com/?i={movie_id}&apikey={self.user_api_key}&?plot=full'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json()

                if response_json == {"Error": "Request limit reached!", "Response": "False"}:
                    logging.info(f"Request limit reached! at {movie_id}")
                    raise ExceptedExtractorFail("Request limit reached!")

                if response_json['Response'] == 'False':
                    raise ValueError("Response == False ? at {}".format(movie_id))

                return await response.json()


class WikiApiExtractor(DataExtractor):
    def __init__(self, *args, **kwargs):
        self.extractor_type = 'wiki'
        super().__init__(*args, **kwargs)
        self.imdb_api_saving_path = self.project_config["api_data_saving_path"]['imdb']
        self.api_url = r'https://en.wikipedia.org/w/api.php'
        self.rest_api_url = 'https://en.wikipedia.org/api/rest_v1'

    async def _build_text_query(self, movie_id):
        file_name = os.path.join(self.imdb_api_saving_path, '{}.json'.format(movie_id))
        if os.path.exists(file_name):
            async with aiofiles.open(file_name, 'r') as jfile:
                    json_file_string = await jfile.read()
            movie_json = json.loads(json_file_string)
            query_info = [movie_json['Title'], movie_json['Year'], movie_json['Type']] # , movie_json['Director']
            return query_info

        else:
            raise ExceptedExtractorFail(f"There is no IMDb data for this {movie_id} IMDb id")

    async def _get_page_id_and_title_by_text_search(self, query_properties):
        """

        :param query_properties: [list] a list of the movie properties to use to build the text query.
        :return:
        """
        # WIKI Search request have a maximum allowed length of 300 chars
        query_properties = self.limit_query_to_maximum_allowed_length(query_properties, max_length=300)

        while query_properties:  # while the list is not empty
            text_to_search_for = ' '.join(query_properties)

            get_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': text_to_search_for
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.api_url, params=get_params) as response:
                    response_json = await response.json()
                    response_status = response.status

                    if 'error' in response_json:
                        raise ValueError(f'"{text_to_search_for}" had an error')

                    if response_json['query']['searchinfo']['totalhits'] == 0:
                        # reconstruct the query_properties with less info so maybe the query will succeed:
                        query_properties = query_properties[:-1]
                    else:
                        best_match = response_json["query"]["search"][0]  # the first one is the best match
                        return best_match["pageid"], best_match["title"]

        raise ExceptedExtractorFail()

    @staticmethod
    def limit_query_to_maximum_allowed_length(query_properties, max_length=300):
        """
        WIKI Search request have a maximum allowed length of 300 chars

        :param query_properties: [list] a list of the movie properties to use to build the text query.
        :param max_length: [int] the maximum size of characters wiki allows to send in a query.
        :return:
        """
        allowed_size_query_properties = []
        total_length = 0
        for query_property in query_properties:
            total_length += len(query_property) + 1  # the additional 1 is for the space between words
            if total_length <= max_length + 1: # the additional 1 is for the extra space after the last word
                allowed_size_query_properties.append(query_property)

        return allowed_size_query_properties

    async def _extract_all_text(self, page_title):
        page_title = page_title.replace(' ', '_')
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.rest_api_url}/page/html/{page_title}?redirect=true") as response:
                response_text = await response.text()
                soup = BeautifulSoup(response_text, 'html.parser')
                return '\n'.join([p.get_text() for p in soup.find_all('p')])

    async def _extract_a_single_id(self, movie_id):
        text_query_parts = await self._build_text_query(movie_id)
        wiki_page_id, wiki_page_title = await self._get_page_id_and_title_by_text_search(text_query_parts)

        text_content = await self._extract_all_text(page_title=wiki_page_title)

        wiki_data = {
            WIKI_TEXT: text_content.lower(),
            'wiki_page_id': wiki_page_id
        }
        return wiki_data
