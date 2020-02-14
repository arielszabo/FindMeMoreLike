import pandas as pd
from tqdm import tqdm

from find_more_like_algorithm.utils import get_imdb_id_prefix_folder_name, VECTORS_CACHE_PATH, \
    get_method_file_last_modified_time, get_file_path_last_modified_time, open_json


def _get_cache_file_path(imdb_id, vectorization_name):
    prefix = get_imdb_id_prefix_folder_name(imdb_id)
    cache_file_path = VECTORS_CACHE_PATH.joinpath(prefix, f"{imdb_id}__{vectorization_name}.json")
    return cache_file_path


def load_cached_data(df, vectorization):
    cached_results = []
    existing_cached_imdb_ids = []
    for imdb_id in tqdm(df.index.tolist(), desc="load cached data"):
        cache_file_path = _get_cache_file_path(imdb_id, vectorization['name'])
        if cache_file_path.exists():
            method_file_last_modified_time = get_method_file_last_modified_time(vectorization["callable"])
            cache_file_file_last_modified_time = get_file_path_last_modified_time(cache_file_path)
            if cache_file_file_last_modified_time >= method_file_last_modified_time:  # TODO hash function
                cached_file_content = open_json(cache_file_path)
                cached_results.append(cached_file_content)
                existing_cached_imdb_ids.append(imdb_id)

    cached_vectors = pd.DataFrame(cached_results, index=existing_cached_imdb_ids)

    df_to_vectorize = df[~df.index.isin(existing_cached_imdb_ids)]

    return df_to_vectorize, cached_vectors


def save_cached_data(df, vectorization):
    for imdb_id in df.index.tolist():
        cache_file_path = _get_cache_file_path(imdb_id, vectorization['name'])
        cache_file_path.parent.mkdir(exist_ok=True, parents=True)
        try:
            df.loc[imdb_id].to_json(cache_file_path)
        except Exception as e:
            print(e, imdb_id)
            continue

