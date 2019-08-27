import os
from tqdm import tqdm
import logging
import pandas as pd
import importlib
import re
from sklearn.feature_extraction.text import CountVectorizer
from .. import utils
from . import text_vectors
import datetime


def tokenizer_comma_separated_strings(full_string):
    separated_strings = re.split(',', full_string)
     # strip the seperated strings becase sometimes there's white-space between the word and the comma:
    return list(map(lambda x: x.strip(), separated_strings))


def extract_from_comma_separated_strings(full_df, column_name):
    full_df.columns = [col.lower() for col in full_df.columns]
    vec = CountVectorizer(tokenizer=tokenizer_comma_separated_strings)

    df_array = vec.fit_transform(full_df[column_name.lower()].fillna('Not_provided')).toarray()
    return pd.DataFrame(df_array, columns=vec.get_feature_names(), index=full_df.index)
    # fields = ['{}_{}'.format(column_name, col).lower() for col in vec.get_feature_names()]

    # return pd.DataFrame(df_array, columns=fields, index=full_df.index)


def rated_vectors(df, rated_col_name):
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
            'TV-14': 'Parents Strongly Cautioned', # not exactly 'Parents Strongly Cautioned' but it's close enough
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

    return pd.get_dummies(df[rated_col_name].apply(_change_rating), dummy_na=True)


def load_data(project_config):
    all_data = []

    imdb_data_path = project_config['api_data_saving_path']['imdb']
    wiki_data_path = project_config['api_data_saving_path']['wiki']
    for file_name in tqdm(os.listdir(imdb_data_path), desc='Loading saved data ...'):
        imdb_data = utils.open_json(os.path.join(imdb_data_path, file_name))
        if file_name in os.listdir(wiki_data_path):
            wiki_data = utils.open_json(os.path.join(wiki_data_path, file_name))

            imdb_data.update(wiki_data)

        else:
            logging.info('{} has no wiki data'.format(file_name))
        all_data.append(imdb_data)

    df = pd.DataFrame(all_data).set_index('imdbID')  # todo: clean this DataFrame, do a 'total text' column etc

    # todo: change this:
    df['text'] = df['text'].fillna('')
    df['full_text'] = df.apply(lambda row: row['text'] + ' ' + row['Plot'], axis=1)

    return df


def create_vectors(project_config):
    df = load_data(project_config)

    vectorization_config = {
        'text_vectors': {
            'callable': text_vectors.get_text_vectors,
            'params': {'doc2vec_model_path': project_config['doc2vec_model_path'], 'text_column_name': 'full_text'}
        },
        'title_vectors': {
            'callable': text_vectors.get_text_vectors,
            'params': {'doc2vec_model_path': project_config['doc2vec_model_path'], 'text_column_name': 'Title'}
        },
        'genre_vectors': {
            'callable': extract_from_comma_separated_strings,
            'params': {'column_name': 'genre'}
        },
        # 'rated_vectors': {
        #     'callable': rated_vectors,
        #     'params': {'rated_col_name': 'Rated'}
        # }
    }

    all_vectors = []
    for vectorization_method in project_config['vectorization']:
        if vectorization_method in vectorization_config:  # todo: Do I need this if? worst case a Key Error will raise which is a good thing in this case
            cache_file_path = os.path.join(project_config['vectors_cache_path'], '{}.pickle'.format('vectorization_method'))
            # if os.path.exists(cache_file_path) and \
            #         datetime.datetime.fromtimestamp(os.path.getmtime(cache_file_path)) >= df['insertion_time'].max():
            #     logging.info("Load cached {}".format(vectorization_method))
            #     vectors = pd.read_pickle(cache_file_path)
            # else:
            logging.info("Starting to create the {}".format(vectorization_method))
            vectorizer = vectorization_config[vectorization_method]

            vectors = vectorizer['callable'](df, **vectorizer['params'])
            vectors.columns = ['{}_{}'.format(vectorization_method, col) for col in vectors.columns]

            all_vectors.append(vectors)

    # for vectorization_method in project_config['vectorization']:
    #     # vectorization_module = importlib.import_module('.{}'.format(vectorization_method),
    #     #                                                package='more_like.vectorization')
    #     # vectors = getattr(vectorization_module, 'get_{}'.format(vectorization_method))(df, project_config)
    #     # all_vectors.append(vectors)
    #     # todo: maybe save this as a dict where key is the vectorization method, and the value is the callable and it's special params?
    #     if vectorization_method == 'text_vectors':
    #         vectors = text_vectors.get_text_vectors(df, doc2vec_model_path=project_config['doc2vec_model_path'])
    #     elif vectorization_method == 'genre':
    #         vectors = extract_from_comma_separated_strings(df, column_name='genre')
    #
    #     else:
    #         continue

        # all_vectors.append(vectors)

    return pd.concat(all_vectors, axis=1, sort=False)  # todo: save them
