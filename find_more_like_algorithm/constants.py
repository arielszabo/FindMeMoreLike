import os
import pathlib

import yaml
from datetime import datetime

IMDB_ID = "imdbID"
INSERTION_TIME = "insertion_time"
FULL_TEXT = "full_text"
WIKI_TEXT = "wiki_text"
root_path = pathlib.Path(__file__).parent.parent.absolute()
RANDOM_SEED = 123
RUN_SIGNATURE_STRING = "run_signature"
TITLE = "Title"
PLOT = "Plot"

LOGFILE_BASE_PATH = "find_me_more_like_logs"
RUN_SIGNATURE = f"find_me_more_like_{datetime.now().strftime('%Y-%m-%d')}"

with root_path.joinpath("project_config.yaml").open() as project_config_yaml_file:
    PROJECT_CONFIG = yaml.load(project_config_yaml_file)
PROJECT_CONFIG[RUN_SIGNATURE_STRING] = RUN_SIGNATURE

RAW_IMDB_DATA_PATH = root_path.joinpath(PROJECT_CONFIG["api_data_saving_path"]["imdb"])
RAW_WIKI_DATA_PATH = root_path.joinpath(PROJECT_CONFIG["api_data_saving_path"]["wiki"])
SIMILAR_LIST_SAVING_PATH = root_path.joinpath(PROJECT_CONFIG['similar_list_saving_path'])
VECTORS_CACHE_PATH = root_path.joinpath(PROJECT_CONFIG['vectors_cache_path'])

SAVING_MOVIES_LIMIT = 150  # TODO change this

keys_config_path = root_path.joinpath(PROJECT_CONFIG['keys_config_path'])
if keys_config_path.exists():
    with keys_config_path.open() as keys_config_yaml_file:
        KEYS_CONFIG = yaml.load(keys_config_yaml_file)
else:
    assert FileNotFoundError(f"Save you OMDb api key in the file {keys_config_path}.\n"
                             f"Please read the README file for more info")

