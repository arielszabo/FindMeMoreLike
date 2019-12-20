import logging
import os
from datetime import datetime

from find_more_like_algorithm import extractors, vectorization, utils, load_and_clean
from find_more_like_algorithm.constants import LOGFILE_BASE_PATH, PROJECT_CONFIG, RUN_SIGNATURE


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

    # # ids_to_query = utils.get_ids_from_web_page('https://www.imdb.com/scary-good/?ref_=nv_sf_sca')
    # all_movies_ids_to_query = utils.open_json("all_movie_ids_to_query.json")

    # GET The data:
    # extractors.IMDBApiExtractor(project_config).extract_data(all_movies_ids_to_query, skip_previously_failed=False)
    # extractors.WikiApiExtractor(project_config).extract_data(all_movies_ids_to_query, skip_previously_failed=False)

    # # Load saved data
    # df = load_and_clean.load_saved_data()
    # logging.info("data loaded")

    # CREATE The Vectors
    df = None
    vectors_df = vectorization.create_vectors(df)
    logging.info("vectors created")

    # CALCULATE similarity
    similarity_df = utils.calculate_similarity(vectors_df, batch=True)
    logging.info("similarity_df created")
    logging.info("Done saving")
