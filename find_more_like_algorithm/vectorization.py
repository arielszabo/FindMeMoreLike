import os
from tqdm import tqdm
import logging
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from find_more_like_algorithm import utils
from find_more_like_algorithm import text_vectors
from find_more_like_algorithm.constants import INSERTION_TIME, root_path
import datetime



def create_vectors(df, project_config):
    vectorization_config = {
        'text_vectors': {
            'callable': text_vectors.get_text_vectors,
            'params': {'doc2vec_model_path': project_config['doc2vec_model_path'], 'text_column_name': full_text}
        },
        'title_vectors': {
            'callable': text_vectors.get_text_vectors,
            'params': {'doc2vec_model_path': project_config['doc2vec_model_path'], 'text_column_name': 'Title'}
        },
        'genre_vectors': {
            'callable': _extract_from_comma_separated_strings,
            'params': {'column_name': 'genre'}
        },
        # 'rated_vectors': {
        #     'callable': _rated_vectors,
        #     'params': {'rated_col_name': 'Rated'}
        # }
    }

    os.makedirs(project_config['vectors_cache_path'], exist_ok=True)
    all_vectors = []
    for vectorization_method in project_config['vectorization']:
        cache_file_path = os.path.join(root_path, project_config['vectors_cache_path'], f"{vectorization_method}.pickle")

        if os.path.exists(cache_file_path):
            cache_file_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file_path))
            if cache_file_modified_time >= df[INSERTION_TIME].max():
                logging.info(f"Load cached '{vectorization_method}'")
                vectors = pd.read_pickle(cache_file_path)
                all_vectors.append(vectors)
                continue

        logging.info(f"Starting to create '{vectorization_method}'")
        vectorization = vectorization_config[vectorization_method]

        vectors = vectorization['callable'](df, **vectorization['params'])
        vectors.columns = [f"{vectorization_method}__{col}" for col in vectors.columns]
        vectors.to_pickle(cache_file_path)

        all_vectors.append(vectors)

    return pd.concat(all_vectors, axis=1, sort=False)  # todo: save them


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
