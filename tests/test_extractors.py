import yaml
import logging
import os
import asyncio
import pytest


from find_more_like_algorithm import extractors, vectorization, utils


def create_folders(testing_config):
    for api, saving_path in testing_config['api_data_saving_path'].items():
        logging.info("raw data from the '{}' api is saved here - {}".format(api, saving_path))
        os.makedirs(saving_path, exist_ok=True)


@pytest.fixture()
def construct_extractors():
    testing_config = _load_test_config()
    create_folders(testing_config)

    imdb_extractor = extractors.IMDBApiExtractor(project_config=testing_config)

    wiki_extractor = extractors.WikiApiExtractor(project_config=testing_config)

    return imdb_extractor, wiki_extractor


def test_get_existing_ids(construct_extractors):
    imdb_extractor, wiki_extractor = construct_extractors
    imdb_extractor.saving_path = os.path.join('tests', 'testing_exisitng_ids_data')  # override this attribute for the test

    assert sorted(imdb_extractor._get_existing_ids()) == sorted(['tt0019254', 'tt10550884', 'tt8242058', 'tt8633296'])


def test_build_text_query(construct_extractors):
    imdb_extractor, wiki_extractor = construct_extractors

    # modify this to the saved_data_for_testing folder path:
    wiki_extractor.imdb_api_saving_path = os.path.join('tests', 'saved_data_for_testing', 'imdb')

    loop = asyncio.get_event_loop()
    async_task = wiki_extractor._build_text_query('tt0019254')
    completed_async_task = loop.run_until_complete(async_task)
    assert completed_async_task == ['The Passion of Joan of Arc', '1928', 'movie']


def test_wiki_adjust_to_maximum_allowed_query_length():
    # This is an static method:

    x = extractors.WikiApiExtractor.limit_query_to_maximum_allowed_length(query_properties=['1234', '5678', '90'],
                                                                          max_length=10)
    assert x == ['1234', '5678']

    x = extractors.WikiApiExtractor.limit_query_to_maximum_allowed_length(query_properties=['1234', '5678', '90'],
                                                                          max_length=100)
    assert x == ['1234', '5678', '90']

    x = extractors.WikiApiExtractor.limit_query_to_maximum_allowed_length(query_properties=['1234', '5678', '90'],
                                                                          max_length=1)
    assert x == []

    x = extractors.WikiApiExtractor.limit_query_to_maximum_allowed_length(query_properties=['1234', '5678', '90'],
                                                                          max_length=6)
    assert x == ['1234']

    x = extractors.WikiApiExtractor.limit_query_to_maximum_allowed_length(query_properties=['1234', '5678', '90'],
                                                                          max_length=4)
    assert x == ['1234']


# def test_extractors(construct_extractors):
#     imdb_extractor, wiki_extractor = construct_extractors
#
#     # IMDB
#
#     extracted_data = imdb_extractor._extract_a_single_id('tt9352780')
#
#     saved_tt9352780 = utils.open_json(os.path.join('tests', 'saved_data_for_testing', 'imdb', 'tt9352780.json'))
#
#     # new_file_path = os.path.join(imdb_extractor.saving_path, 'tt9352780.json')
#     # extracted_tt9352780 = utils.open_json(new_file_path)
#     assert sorted(extracted_data.keys()) == sorted(saved_tt9352780.keys())
#     for key, value in extracted_data.items():
#         assert saved_tt9352780[key] == value
#     # assert json.dumps(extracted_data, sort_keys=True) == json.dumps(saved_tt9352780, sort_keys=True)
#
#
#     # todo: add more imdb ids_to_query
#
#
#
#     # WIKI
#     wiki_extractor.extract_data(ids_to_query=['tt0019254', 'tt9352780', 'tt10550884'])
#
#     extracted_wiki, saved_wiki, new_file_path = _extract_and_load(tt='tt0019254', extractor_instance=wiki_extractor)
#     assert json.dumps(extracted_wiki, sort_keys=True) == json.dumps(saved_wiki, sort_keys=True)
#     os.remove(new_file_path)  # delete the new file so next time it will need to be queried
#
#     extracted_wiki, saved_wiki, new_file_path = _extract_and_load(tt='tt9352780', extractor_instance=wiki_extractor)
#     assert json.dumps(extracted_wiki, sort_keys=True) == json.dumps(saved_wiki, sort_keys=True)
#     os.remove(new_file_path)  # delete the new file so next time it will need to be queried
#
#     extracted_wiki, saved_wiki, new_file_path = _extract_and_load(tt='tt10550884', extractor_instance=wiki_extractor)
#     assert json.dumps(extracted_wiki, sort_keys=True) == json.dumps(saved_wiki, sort_keys=True)
#     os.remove(new_file_path)  # delete the new file so next time it will need to be queried


def _load_test_config():
    with open(os.path.join('tests', 'testing_config.yaml'), 'r') as yfile:
        testing_config = yaml.load(yfile, Loader=yaml.FullLoader)
    return testing_config

#
# def _extract_and_load(tt, extractor_instance):
#     saved_wiki = utils.open_json(os.path.join('tests', 'saved_data_for_testing', 'wiki', '{}.json'.format(tt)))
#     new_file_path = os.path.join(extractor_instance.saving_path, '{}.json'.format(tt))
#     extracted_wiki = utils.open_json(new_file_path)
#
#     return extracted_wiki, saved_wiki, new_file_path