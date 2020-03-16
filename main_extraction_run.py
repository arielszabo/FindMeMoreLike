import logging
import os
from find_more_like_algorithm import extractors, utils
from find_more_like_algorithm.constants import LOGFILE_BASE_PATH
from find_more_like_algorithm.utils import RUN_SIGNATURE, PROJECT_CONFIG

os.makedirs(LOGFILE_BASE_PATH, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOGFILE_BASE_PATH, f"{RUN_SIGNATURE}.log")),
        logging.StreamHandler()
    ])


if __name__ == '__main__':
    logging.info(PROJECT_CONFIG)

    # ids_to_query = utils.get_ids_from_web_page('https://www.imdb.com/scary-good/?ref_=nv_sf_sca')
    all_movies_ids_to_query = utils.open_json("all_movie_ids_to_query.json")
    # TODO: find out new movies

    # GET The data:
    extractors.IMDBApiExtractor(PROJECT_CONFIG).extract_data(all_movies_ids_to_query, skip_previously_failed=True)
    extractors.WikiApiExtractor(PROJECT_CONFIG).extract_data(all_movies_ids_to_query, skip_previously_failed=True)
