import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string
import re
import numpy as np
from gensim.models import Doc2Vec
from find_more_like_algorithm.constants import RANDOM_SEED
from tqdm import tqdm
np.random.seed(RANDOM_SEED)


def get_text_vectors(df, text_column_name, doc2vec_model_path):
    doc2vec = Doc2Vec.load(doc2vec_model_path)

    tqdm.pandas(desc=f"extract doc2vec features for {text_column_name}")
    vectors_df = df.progress_apply(infer_doc2vec_vector,
                                   axis=1,
                                   text_column_name=text_column_name,
                                   doc2vec_model=doc2vec,
                                   result_type='expand')  # progress_apply is apply with tqdm progress bar
    vectors_df.columns = ['doc2vec__{}'.format(col) for col in vectors_df.columns]
    return vectors_df


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


def infer_doc2vec_vector(row, text_column_name, doc2vec_model):
    text = row[text_column_name]
    clean_token_text = token_text(full_text=text,
                                  remove_stop_words=False, # todo: maybe it's better if this would be False
                                  remove_punctuations=True,
                                  remove_if_not_alpha=True,
                                  stem_word=False)
    return doc2vec_model.infer_vector(clean_token_text).tolist() # todo: , epochs=1000 ?


