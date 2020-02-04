import pandas as pd
from find_more_like_algorithm import vectorization
from find_more_like_algorithm.vectorization import text_vectors


def test_tokenizer_comma_separated_strings():
    assert vectorization._tokenizer_comma_separated_strings('this, is good') == ['this', 'is good']
    assert vectorization._tokenizer_comma_separated_strings('with , 2spaces') == ['with', '2spaces']
    assert vectorization._tokenizer_comma_separated_strings('with, space') == ['with', 'space']
    assert vectorization._tokenizer_comma_separated_strings('with ,space') == ['with', 'space']
    assert vectorization._tokenizer_comma_separated_strings('with ,space') == ['with', 'space']
    assert vectorization._tokenizer_comma_separated_strings('nocomma') == ['nocomma']
    assert vectorization._tokenizer_comma_separated_strings('nocomma,') == ['nocomma', '']
    assert vectorization._tokenizer_comma_separated_strings(',nocomma') == ['', 'nocomma']
    assert vectorization._tokenizer_comma_separated_strings('no,space') == ['no', 'space']
    assert vectorization._tokenizer_comma_separated_strings('no,space ,1space , 2spaces') == ['no', 'space',
                                                                                             '1space', '2spaces']


def test_extract_from_comma_separated_strings():
    expected_output_dict = {'four': {0: 0, 1: 0, 2: 0, 3: 0, 4: 1},
                            'not_provided': {0: 0, 1: 0, 2: 0, 3: 1, 4: 0},
                            'one': {0: 1, 1: 1, 2: 1, 3: 0, 4: 1},
                            'three': {0: 0, 1: 0, 2: 1, 3: 0, 4: 1},
                            'two': {0: 0, 1: 1, 2: 1, 3: 0, 4: 1}}

    df = pd.DataFrame({'this_column': ['one', 'one, two', 'one, two , three', None, 'one, two , three,four']})
    extracted_df = vectorization._extract_from_comma_separated_strings(df, column_name='this_column')
    extracted_dict = extracted_df.to_dict()
    assert extracted_dict == expected_output_dict


def test_token_text():
    assert text_vectors.token_text(full_text='this is a sample',
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=False) == ['sample']

    assert text_vectors.token_text(full_text='this is a sample',
                                    remove_stop_words=False,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=False) == ['this', 'is', 'a', 'sample']

    assert text_vectors.token_text(full_text='this is a sample with not only stop words',
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=False) == ['sample', 'stop', 'words']

    assert text_vectors.token_text(full_text='Hello man',
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=False) == ['hello', 'man']

    assert text_vectors.token_text(full_text='Hello man, this is cool.',
                                    remove_stop_words=True,
                                    remove_punctuations=False,
                                    remove_if_not_alpha=False,
                                    stem_word=False) == ['hello', 'man', ',', 'cool', '.']

    assert text_vectors.token_text(full_text='Hello man, this is c00l.',
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=False,
                                    stem_word=False) == ['hello', 'man', 'c00l']

    assert text_vectors.token_text(full_text='Hello man, this is c00l.',
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=False) == ['hello', 'man']

    assert text_vectors.token_text(full_text="let's not use stemming here",
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=False) == ['let', 'use', 'stemming']

    assert text_vectors.token_text(full_text="let's not use stemming here",
                                    remove_stop_words=True,
                                    remove_punctuations=True,
                                    remove_if_not_alpha=True,
                                    stem_word=True) == ['let', 'use', 'stem']