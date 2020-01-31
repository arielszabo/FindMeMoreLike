import os
import pathlib

from tqdm import tqdm
import logging
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from find_more_like_algorithm import text_vectors
from find_more_like_algorithm.constants import INSERTION_TIME, root_path, FULL_TEXT, PROJECT_CONFIG, TITLE
from datetime import datetime
import multiprocessing



def create_vectors(df):
    vectorizations_config = [
        {
            'name': 'text_vectors',
            'callable': text_vectors.get_text_vectors,
            'params': {'doc2vec_model_path': PROJECT_CONFIG['doc2vec_model_path'], 'text_column_name': FULL_TEXT}
        },
        {
            'name': 'title_vectors',
            'callable': text_vectors.get_text_vectors,
            'params': {'doc2vec_model_path': PROJECT_CONFIG['doc2vec_model_path'], 'text_column_name': TITLE}
        },
        {
            'name': 'genre_vectors',
            'callable': _extract_from_comma_separated_strings,
            'params': {'column_name': 'genre'}
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
    cache_file_path = pathlib.Path(root_path, PROJECT_CONFIG['vectors_cache_path'], f"{vectorization['name']}.pickle")
    if cache_file_path.exists():
    # TODO use this on server ->
    #     logging.info(f"Load cached '{vectorization_method}'")
    #     vectors = pd.read_pickle(cache_file_path)
    #     return vectors
    # TODO use this on server <-
        cache_file_modified_time = datetime.fromtimestamp(cache_file_path.stat().st_mtime)
        if cache_file_modified_time >= df[INSERTION_TIME].max():
            logging.info(f"Load cached {vectorization['name']} vectors")
            vectors = pd.read_pickle(str(cache_file_path))
            return vectors

    logging.info(f"Starting to create {vectorization['name']} vectors")
    vectors = vectorization['callable'](df, **vectorization['params'])
    vectors.columns = [f"{vectorization['name']}__{col}" for col in vectors.columns]
    vectors.to_pickle(cache_file_path)
    return vectors


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
