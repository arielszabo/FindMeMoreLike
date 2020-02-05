import json
import math
import os
import pathlib
import re
from datetime import datetime
from importlib import import_module
import requests
import yaml
from bs4 import BeautifulSoup

from find_more_like_algorithm.constants import IMDB_ID, TITLE, IMDB_ID_REGEX_PATTERN, RUN_SIGNATURE_STRING

ROOT_PATH = pathlib.Path(__file__).parent.parent.absolute()
RUN_SIGNATURE = f"find_me_more_like_{datetime.now().strftime('%Y-%m-%d')}"


if "PYTEST_CURRENT_TEST" in os.environ or 'TRAVIS' in os.environ:
    PROJECT_CONFIG_FILE_PATH = ROOT_PATH.joinpath("tests", "testing_config.yaml")
else:
    PROJECT_CONFIG_FILE_PATH = ROOT_PATH.joinpath("project_config.yaml")

with PROJECT_CONFIG_FILE_PATH.open() as project_config_yaml_file:
    PROJECT_CONFIG = yaml.load(project_config_yaml_file)
PROJECT_CONFIG[RUN_SIGNATURE_STRING] = RUN_SIGNATURE

RAW_IMDB_DATA_PATH = ROOT_PATH.joinpath(PROJECT_CONFIG["api_data_saving_path"]["imdb"])
RAW_WIKI_DATA_PATH = ROOT_PATH.joinpath(PROJECT_CONFIG["api_data_saving_path"]["wiki"])
SIMILAR_LIST_SAVING_PATH = ROOT_PATH.joinpath(PROJECT_CONFIG['similar_list_saving_path'])
VECTORS_CACHE_PATH = ROOT_PATH.joinpath(PROJECT_CONFIG['vectors_cache_path'])
DOC2VEC_MODEL_PATH = ROOT_PATH.joinpath(PROJECT_CONFIG['doc2vec_model_path'])
keys_config_path = ROOT_PATH.joinpath(PROJECT_CONFIG['keys_config_path'])
with keys_config_path.open() as keys_config_yaml_file:
    KEYS_CONFIG = yaml.load(keys_config_yaml_file)


def open_json(full_file_path):
    try:
        with open(full_file_path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(str(e), full_file_path)
        raise e


def open_yaml(full_file_path):
    with open(full_file_path, 'r') as yaml_file:
        return yaml.load(yaml_file)


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
        for idx in re.findall(IMDB_ID_REGEX_PATTERN, str(link)):
            ids.add(idx)

    return ids


def generate_list_chunks(list_, chunk_size=None, chunks_amount=None):
    if chunk_size is None and chunks_amount is None:
        raise ValueError("both chunk_size and chunks_amount can't be None at the same time, please pass one of them")
    if chunk_size is not None and chunks_amount is not None:
        raise ValueError("both chunk_size and chunks_amount were passed at the same time, please pass only one of them")

    if chunks_amount is not None:
        chunk_size = math.ceil(len(list_) / chunks_amount)

    i = 0
    while True:
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size
        list_part = list_[start_index: end_index]
        i += 1
        yield list_part
        if end_index >= len(list_):
            break


def get_imdb_id_prefix_folder_name(imdb_id, prefix_length=4):
    return imdb_id[:prefix_length]


def _get_all_existing_imdb_ids():
    all_saved_files = RAW_IMDB_DATA_PATH.rglob('*/*.json')

    existing_ids = []
    for saved_file_path in all_saved_files:
        saved_file_name = saved_file_path.name
        search_result = re.search(f'({IMDB_ID_REGEX_PATTERN}).json', saved_file_name)
        if search_result:
            existing_ids.append(search_result.group(1))
    return existing_ids


def create_title_and_id_mapping():
    title_and_id = []
    for similar_list_file_path in SIMILAR_LIST_SAVING_PATH.rglob("*/*.json"):
        imdb_id = similar_list_file_path.stem
        imdb_id_prefix = get_imdb_id_prefix_folder_name(imdb_id)
        raw_imdb_file_path = RAW_IMDB_DATA_PATH.joinpath(imdb_id_prefix, similar_list_file_path.name)
        with raw_imdb_file_path.open() as raw_imdb_file:
            raw_imdb_file_content = json.load(raw_imdb_file)

        title_and_id.append({
            TITLE: raw_imdb_file_content[TITLE],
            IMDB_ID: imdb_id
        })

    title_and_id_mapping_path = pathlib.Path(ROOT_PATH, "webapp", "static", "title_and_id_mapping.json")
    # create_title_and_id_mapping_path = pathlib.Path(ROOT_PATH, "webapp", "static", "title_and_id_mapping__old.json")
    with title_and_id_mapping_path.open("w") as title_and_id_mapping_file:
        json.dump(title_and_id, title_and_id_mapping_file)


def get_method_file_last_modified_time(method_object):
    # TODO maybe find the latest time of all import files ?
    module_name = method_object.__module__
    module_object = import_module(module_name)
    module_file_name = module_object.__file__
    file_last_modified_timestamp = pathlib.Path(module_file_name).lstat().st_mtime
    file_last_modified_datetime = datetime.fromtimestamp(file_last_modified_timestamp)
    return file_last_modified_datetime


def get_file_path_last_modified_time(file_path):
    if not isinstance(file_path, pathlib.Path):
        file_path = pathlib.Path(file_path)
    file_last_modified_timestamp = file_path.lstat().st_mtime
    file_last_modified_datetime = datetime.fromtimestamp(file_last_modified_timestamp)
    return file_last_modified_datetime
