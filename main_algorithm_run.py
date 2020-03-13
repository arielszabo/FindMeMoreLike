import logging
import os
from find_more_like_algorithm import vectorization, load_and_clean, similarity
from find_more_like_algorithm.constants import LOGFILE_BASE_PATH
from find_more_like_algorithm.utils import create_available_titles_and_title_to_id_mapping, RUN_SIGNATURE, PROJECT_CONFIG

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

    # Load saved data
    df = load_and_clean.load_saved_data()
    logging.info(f"data of shape {df.shape} was loaded")

    # CREATE The Vectors
    # df = None
    vectors_df = vectorization.create_vectors(df)
    logging.info("vectors created")

    # CALCULATE similarity
    similarity_df = similarity.calculate(vectors_df, use_multiprocessing=False)
    logging.info("similarity_df created")
    logging.info("Done saving")

    # For the webapp
    create_available_titles_and_title_to_id_mapping()
