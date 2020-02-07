import logging
import pathlib
import re

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

from find_more_like_algorithm import text_vectors
from find_more_like_algorithm.constants import FULL_TEXT, TITLE
from find_more_like_algorithm.cache_handler import load_cached_data, save_cached_data


def create_vectors(df):
    vectorizations_config = [
        {
            'name': 'text_vectors',
            'callable': text_vectors.get_text_vectors,
            'params': {
                'text_column_name': FULL_TEXT
            },
            'cache': True
        },
        {
            'name': 'title_vectors',
            'callable': text_vectors.get_text_vectors,
            'params': {
                'text_column_name': TITLE
            },
            'cache': True
        },
        {
            'name': 'genre_vectors',
            'callable': _extract_from_comma_separated_strings,
            'params': {
                'column_name': 'Genre'
            },
            'cache': False
        },
        # {
        #     'name': 'rated_vectors',
        #     'callable': _rated_vectors,
        #     'params': {
        #         'rated_column_name': 'Rated'
        #     },
        #     'cache': False
        # }
    ]

    all_vectors = []
    for vectorization in vectorizations_config:
        result = apply_vectorization(df, vectorization)
        all_vectors.append(result)

    return pd.concat(all_vectors, axis=1, sort=False)


def apply_vectorization(df, vectorization):
    if vectorization['cache']:
        df_to_vectorize, cached_vectors = load_cached_data(df, vectorization)
        logging.info(f"{cached_vectors.shape[0]} of {df.shape[0]} {vectorization['name']} were found in cache")

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
    logging.info(f"Starting to create {vectorization['name']} on {df.shape[0]} rows")
    vectors = vectorization['callable'](df, **vectorization['params'])
    vectors.columns = [f"{vectorization['name']}__{col}" for col in vectors.columns]
    if vectorization['cache']:
        save_cached_data(vectors, vectorization)
    return vectors


def _rated_vectors(df, rated_column_name):
    standardized_rated_column_series = df[rated_column_name].apply(_standardized_rated_column)
    return pd.get_dummies(standardized_rated_column_series, dummy_na=True)  # TODO: maybe do a pca ?


def _tokenizer_comma_separated_strings(full_string):
    separated_strings = re.split(',', full_string)
     # strip the separated strings because sometimes there's white-space between the word and the comma:
    stripped_separated_strings = [separated_string.strip() for separated_string in separated_strings]
    return stripped_separated_strings


def _extract_from_comma_separated_strings(df, column_name):
    count_vectorizer = CountVectorizer(tokenizer=_tokenizer_comma_separated_strings)

    df_sparse_array = count_vectorizer.fit_transform(df[column_name].fillna('not_provided'))
    df_dense_array = df_sparse_array.toarray()
    feature_names = count_vectorizer.get_feature_names()

    vectored_df = pd.DataFrame(df_dense_array, columns=feature_names, index=df.index)
    return vectored_df


def _standardized_rated_column(movie_rating):
    ratings_converter = {
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
        'Passed': 'PASSED',
        'UNRATED': 'Not Rated'
    }

    if movie_rating not in ratings_converter:
        raise ValueError('This movie rating: {} does not exist in the converter...'.format(movie_rating))
    else:
        return ratings_converter[movie_rating]
