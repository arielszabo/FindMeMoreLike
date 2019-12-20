import os
import yaml
from datetime import datetime

IMDB_ID = "imdbID"
INSERTION_TIME = "insertion_time"
FULL_TEXT = "full_text"
WIKI_TEXT = "wiki_text"
root_path = os.path.dirname(os.path.dirname(__file__))
RANDOM_SEED = 123
RUN_SIGNATURE_STRING = "run_signature"

LOGFILE_BASE_PATH = "find_me_more_like_logs"
RUN_SIGNATURE = f"find_me_more_like_{datetime.now().strftime('%Y-%m-%d')}"

with open(os.path.join(root_path, "project_config.yaml"), 'r') as yaml_file:
    PROJECT_CONFIG = yaml.load(yaml_file)
PROJECT_CONFIG[RUN_SIGNATURE_STRING] = RUN_SIGNATURE
