import os
import pathlib

from tqdm import tqdm
import logging
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from find_more_like_algorithm import text_vectors
from find_more_like_algorithm.constants import INSERTION_TIME, root_path, FULL_TEXT, PROJECT_CONFIG
from datetime import datetime
import multiprocessing

from find_more_like_algorithm.utils import get_imdb_id_prefix_folder_name, open_json


def create_vectors(df):
    vectorizations_config = [
        {
            'name': 'text_vectors',
            'callable': text_vectors.get_text_vectors,
            'params': {
                'doc2vec_model_path': PROJECT_CONFIG['doc2vec_model_path'],
                'text_column_name': FULL_TEXT
            },
            'cache': True
        },
        {
            'name': 'title_vectors',
            'callable': text_vectors.get_text_vectors,
            'params': {
                'doc2vec_model_path': PROJECT_CONFIG['doc2vec_model_path'],
                'text_column_name': 'title'
            },
            'cache': True
        },
        {
            'name': 'genre_vectors',
            'callable': _extract_from_comma_separated_strings,
            'params': {
                'column_name': 'genre'
            }
        },
        # 'rated_vectors': {
        #     'callable': _rated_vectors,
        #     'params': {'rated_col_name': 'rated'}
        # }
    ]

    vectors_cache_path = pathlib.Path(root_path, PROJECT_CONFIG['vectors_cache_path'])
    vectors_cache_path.mkdir(parents=True, exist_ok=True)

    all_vectors = []
    for vectorization in vectorizations_config:
        if vectorization["name"] in PROJECT_CONFIG['vectorization']:
            result = apply_vectorization(df, vectorization)
            all_vectors.append(result)


    return pd.concat(all_vectors, axis=1, sort=False)


def apply_vectorization(df, vectorization):
    if vectorization['cache']:
        df_to_vectorize, cached_vectors = _load_cached_data(df, vectorization)

        if df_to_vectorize.empty:
            return cached_vectors
        else:
            vectors = _apply_vectorization(df_to_vectorize, vectorization)

            vectors_with_cache = pd.concat([cached_vectors, vectors])
            return vectors_with_cache.loc[df.index]
    else:
        vectors = _apply_vectorization(df, vectorization)
        return vectors


def _apply_vectorization(df, vectorization):
    logging.info(f"Starting to create {vectorization['name']} vectors on {df.shape} rows")
    vectors = vectorization['callable'](df, **vectorization['params'])
    vectors.columns = [f"{vectorization['name']}__{col}" for col in vectors.columns]
    if vectorization['cache']:
        _save_cached_data(vectors, vectorization)
    return vectors


def _get_cache_file_path(imdb_id, vectorization_name):
    prefix = get_imdb_id_prefix_folder_name(imdb_id)
    # TODO use VECTORS_CACHE_PATH
    cache_file_path = pathlib.Path(root_path, PROJECT_CONFIG['vectors_cache_path'], prefix, f"{imdb_id}__{vectorization_name}.json")
    return cache_file_path


def _load_cached_data(df, vectorization):
    cached_results = []
    existing_cached_imdb_ids = []
    for imdb_id in df.index.tolist():
        cache_file_path = _get_cache_file_path(imdb_id, vectorization['name'])
        if cache_file_path.exists():  # TODO use time
            imdb_id_cached_results = open_json(cache_file_path)
            cached_results.append(imdb_id_cached_results)
            existing_cached_imdb_ids.append(imdb_id)

    cached_vectors = pd.DataFrame(cached_results, index=existing_cached_imdb_ids)

    df_to_vectorize = df[~df.index.isin(existing_cached_imdb_ids)]

    return df_to_vectorize, cached_vectors


def _save_cached_data(df, vectorization):
    for imdb_id in df.index.tolist():
        cache_file_path = _get_cache_file_path(imdb_id, vectorization['name'])
        cache_file_path.parent.mkdir(exist_ok=True, parents=True)
        df.loc[imdb_id].to_json(cache_file_path)


def _rated_vectors(df, rated_column_name):
    return pd.get_dummies(df[rated_column_name].apply(_change_rating), dummy_na=True)


def _tokenizer_comma_separated_strings(full_string):
    separated_strings = re.split(',', full_string)
     # strip the separated strings because sometimes there's white-space between the word and the comma:
    stripped_separated_strings = [separated_string.strip() for separated_string in separated_strings]
    return stripped_separated_strings


def _extract_from_comma_separated_strings(df, column_name):
    count_vectorizer = CountVectorizer(tokenizer=_tokenizer_comma_separated_strings)

    df_sparse_array = count_vectorizer.fit_transform(df[column_name.lower()].fillna('not_provided'))
    df_dense_array = df_sparse_array.toarray()
    feature_names = count_vectorizer.get_feature_names()
    # feature_names = [f"{column_name}_{col}".lower() for col in count_vectorizer.get_feature_names()]  # todo: why comment out?

    vectored_df = pd.DataFrame(df_dense_array, columns=feature_names, index=df.index)
    return vectored_df


def _change_rating(movie_rating):
    # what todo with UNRATED is it as Not Rated?
    ratings_convertor = {
        'R': 'Restricted',
        'G': 'General Audiences',
        'TV-Y': 'General Audiences',
        'TV-Y7': 'General Audiences',  # this is not exactly 'General Audiences' but it's close enough
        'TV-Y7-FV': 'General Audiences',  # this is not exactly 'General Audiences' but it's close enough
        'TV-G': 'General Audiences',
        'PG': 'Parental Guidance Suggested',
        'TV-PG': 'Parental Guidance Suggested',
        'GP': 'Parental Guidance Suggested',
        'M/PG': 'Parental Guidance Suggested',
        'M': 'Parental Guidance Suggested',
        'PG-13': 'Parents Strongly Cautioned',
        'TV-14': 'Parents Strongly Cautioned',  # not exactly 'Parents Strongly Cautioned' but it's close enough
        'NC-17': 'Adults Only',
        'TV-MA': 'Adults Only',
        'NR': 'Not Rated',
        'X': 'Adults Only',
        'N/A': None,
        'NOT RATED': 'Not Rated',
        'Not Rated': 'Not Rated',
        'APPROVED': 'APPROVED',
        'PASSED': 'PASSED',
        'UNRATED': 'UNRATED'

    }

    if movie_rating not in ratings_convertor:
        raise ValueError('This movie rating: {} does not exist in the convertor...'.format(movie_rating))
    else:
        return ratings_convertor[movie_rating]
