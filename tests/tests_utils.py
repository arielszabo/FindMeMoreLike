from find_more_like_algorithm.utils import generate_list_chunks


def test_generate_list_chunks():
    list_of_chunk = list(generate_list_chunks([1, 2, 3, 4, 5], chunk_size=2))
    assert len(list_of_chunk) == 3
    assert list_of_chunk[0] == [1, 2]
    assert list_of_chunk[1] == [3, 4]
    assert list_of_chunk[2] == [5]

    list_of_chunk = list(generate_list_chunks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], chunk_size=3))
    assert len(list_of_chunk) == 4
    assert list_of_chunk[0] == [1, 2, 3]
    assert list_of_chunk[1] == [4, 5, 6]

    list_of_chunk = list(generate_list_chunks([1, 2, 3, 4, 5], chunks_amount=2))
    assert len(list_of_chunk) == 2
    assert list_of_chunk[0] == [1, 2, 3]
    assert list_of_chunk[1] == [4, 5]

    list_of_chunk = list(generate_list_chunks([1, 2, 3, 4, 5, 6], chunks_amount=2))
    assert len(list_of_chunk) == 2
    assert list_of_chunk[0] == [1, 2, 3]
    assert list_of_chunk[1] == [4, 5, 6]

    list_of_chunk = list(generate_list_chunks([1, 2, 3, 4, 5, 6], chunks_amount=7))
    assert len(list_of_chunk) == 6
    assert list_of_chunk[0] == [1]
    assert list_of_chunk[-1] == [6]

    list_of_chunk = list(generate_list_chunks([1, 2, 3, 4, 5, 6], chunk_size=7))
    assert len(list_of_chunk) == 1
    assert list_of_chunk[0] == [1, 2, 3, 4, 5, 6]
