import os
import nltk
import pandas as pd
from find_more_like_algorithm.utils import generate_list_chunks
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string
import re
import numpy as np
from gensim.models import Doc2Vec
from find_more_like_algorithm.constants import RANDOM_SEED, DOC2VEC_MODEL_PATH
from tqdm import tqdm
import multiprocessing
np.random.seed(RANDOM_SEED)
nltk.download('stopwords')
nltk.download('punkt')


def get_text_vectors(df, text_column_name):
    number_of_process = os.cpu_count() - 2
    batch_df_index_lists = generate_list_chunks(df.index.tolist(), chunks_amount=number_of_process)

    text_series_batches = (df.loc[batch_index_list, text_column_name] for batch_index_list in batch_df_index_lists)

    with multiprocessing.Pool(number_of_process) as pool:
        results = tqdm(iterable=pool.imap(get_text_vectors_on_batch_text_series, iterable=text_series_batches),
                       total=number_of_process)
        vectors_batch_df_list = list(results)

    vectors_df = pd.concat(vectors_batch_df_list)
    assert sorted(vectors_df.index) == sorted(df.index)
    vectors_df = vectors_df.loc[vectors_df.index]

    return vectors_df


def get_text_vectors_on_batch_text_series(batch_text_series):
    doc2vec = Doc2Vec.load(str(DOC2VEC_MODEL_PATH))
    list_of_vectors = batch_text_series.apply(infer_doc2vec_vector, doc2vec_model=doc2vec).tolist()
    vectors_batch_df = pd.DataFrame(list_of_vectors, index=batch_text_series.index)
    vectors_batch_df.columns = ['doc2vec__{}'.format(col) for col in vectors_batch_df.columns]

    return vectors_batch_df


def token_text(full_text, remove_stop_words=True, remove_punctuations=True, remove_if_not_alpha=True, stem_word=False):
    porter = PorterStemmer()

    stop_words = set(stopwords.words('english'))
    punctuations = list(string.punctuation)

    tokenize_words = []
    full_text = re.sub(r'-+', ' ', full_text)
    for sentence in nltk.sent_tokenize(full_text.lower()):
        for word in nltk.word_tokenize(sentence):
            if word in stop_words and remove_stop_words == True:
                continue
            if word in punctuations and remove_punctuations == True:
                continue
            if not word.isalpha() and remove_if_not_alpha == True:  # if not all characters in the string are alphabetic
                continue
            if stem_word:
                word = porter.stem(word)

            tokenize_words.append(word)
    return tokenize_words


def infer_doc2vec_vector(text, doc2vec_model):
    clean_token_text = token_text(full_text=text,
                                  remove_stop_words=False, # todo: maybe it's better if this would be False
                                  remove_punctuations=True,
                                  remove_if_not_alpha=True,
                                  stem_word=False)
    return doc2vec_model.infer_vector(clean_token_text).tolist() # todo: , epochs=1000 ?


