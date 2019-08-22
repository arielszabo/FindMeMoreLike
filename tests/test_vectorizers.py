import json
import pandas as pd
from more_like import vectorization, utils

def test_tokenizer_comma_separated_strings():
    assert vectorization.tokenizer_comma_separated_strings('this, is good') == ['this', 'is good']
    assert vectorization.tokenizer_comma_separated_strings('with , 2spaces') == ['with', '2spaces']
    assert vectorization.tokenizer_comma_separated_strings('with, space') == ['with', 'space']
    assert vectorization.tokenizer_comma_separated_strings('with ,space') == ['with', 'space']
    assert vectorization.tokenizer_comma_separated_strings('with ,space') == ['with', 'space']
    assert vectorization.tokenizer_comma_separated_strings('nocomma') == ['nocomma']
    assert vectorization.tokenizer_comma_separated_strings('nocomma,') == ['nocomma', '']
    assert vectorization.tokenizer_comma_separated_strings(',nocomma') == ['', 'nocomma']
    assert vectorization.tokenizer_comma_separated_strings('no,space') == ['no', 'space']
    assert vectorization.tokenizer_comma_separated_strings('no,space ,1space , 2spaces') == ['no', 'space',
                                                                                             '1space', '2spaces']


def test_extract_from_comma_separated_strings():
    df = pd.DataFrame({'this_column': ['one', 'one, two', 'one, two , three', None, 'one, two , three,four']})
    extracted_df = vectorization.extract_from_comma_separated_strings(df, column_name='this_column')
    assert extracted_df.to_dict() == {'this_column_four': {0: 0, 1: 0, 2: 0, 3: 0, 4: 1},
                                      'this_column_not_provided': {0: 0, 1: 0, 2: 0, 3: 1, 4: 0},
                                      'this_column_one': {0: 1, 1: 1, 2: 1, 3: 0, 4: 1},
                                      'this_column_three': {0: 0, 1: 0, 2: 1, 3: 0, 4: 1},
                                      'this_column_two': {0: 0, 1: 1, 2: 1, 3: 0, 4: 1}}