import asyncio
import gc
import pathlib

import aiofiles
import requests
from bs4 import BeautifulSoup
import re
import os
import json
import pandas as pd
from sklearn import metrics
from tqdm import tqdm
import yaml
import numpy as np
import glob
from find_more_like_algorithm.constants import PROJECT_CONFIG, SAVING_MOVIES_LIMIT, root_path, IMDB_ID, TITLE, \
    SIMILAR_LIST_SAVING_PATH, RAW_IMDB_DATA_PATH


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
        for idx in re.findall(r'tt\d+', str(link)):
            ids.add(idx)

    return ids


def generate_list_chunks(list_, chunk_size):
    i = 0
    while True:
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size
        list_part = list_[start_index : end_index]
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
        search_result = re.search(r'(tt\d+).json', saved_file_name)
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

    title_and_id_mapping_path = pathlib.Path(root_path, "webapp", "static", "title_and_id_mapping.json")
    # create_title_and_id_mapping_path = pathlib.Path(root_path, "webapp", "static", "title_and_id_mapping__old.json")
    with title_and_id_mapping_path.open("w") as title_and_id_mapping_file:
        json.dump(title_and_id, title_and_id_mapping_file)


def get_file_paths_with_empty_plot_data():
    empty_plot_file_paths = []
    for raw_imdb_file_path in RAW_IMDB_DATA_PATH.glob("*/*.json"):
        with raw_imdb_file_path.open() as raw_imdb_file:
            raw_imdb_file_content = json.load(raw_imdb_file)
            if raw_imdb_file_content["Plot"].lower().strip() == "n/a":
                empty_plot_file_paths.append(raw_imdb_file_path)

    return empty_plot_file_paths
