import yaml
import logging
import os
from datetime import datetime

from find_more_like_algorithm import extraction, vectorization, utils
from find_more_like_algorithm.constants import root_path

logfile_base_path = "find_me_more_like_logs"
run_signature = f"find_me_more_like_{datetime.now().strftime('%Y-%m-%d')}"

os.makedirs(logfile_base_path, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(logfile_base_path, f"{run_signature}.log")),
        logging.StreamHandler()
    ])


if __name__ == '__main__':

    project_config = utils.open_yaml(os.path.join(root_path, "project_config.yaml"))

    logging.info(project_config)

    # ids_to_query = utils.get_ids_from_web_page('https://www.imdb.com/scary-good/?ref_=nv_sf_sca')
    all_movies_ids_to_query = utils.open_json("all_movie_ids_to_query.json")

    # GET The data:
    extraction.IMDBApiExtractor(project_config).extract_data(all_movies_ids_to_query)
    extraction.WikiApiExtractor(project_config).extract_data(all_movies_ids_to_query)


    # CREATE The Vectors
    vectors_df = vectorization.create_vectors(project_config)

    # CALCULATE similarity
    similarity_df = utils.calculate_similarity(vectors_df, project_config)

    utils.save_similarity_measures(similarity_df, project_config=project_config)
