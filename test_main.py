from fastapi.testclient import TestClient
from main import app
from utils import create_default_trie, is_word_in_trie, trie_to_list_of_words

client = TestClient(app)


def test_add_words():

    # populate the storage by adding all words
    storage = create_default_trie()
    words = trie_to_list_of_words(storage)
    response = client.post('/words.json', json={'words': words})
    assert response.status_code == 201
    assert len(client.app.storage) > 0  # == 53


def test_delete_word():

    word = 'dummy_word'

    # populate the storage with single word
    response = client.post('/words.json', json={'words': [word]})
    assert response.status_code == 201
    assert is_word_in_trie(client.app.storage, word)

    # delete the word
    response = client.delete(f'/words/{word}.json')
    assert response.status_code == 204
    assert not is_word_in_trie(client.app.storage, word)


def test_delete_all_words():
    response = client.delete('/words.json')
    assert response.status_code == 204
    assert len(client.app.storage) == 0

    # reset app.storage to default for other tests
    test_add_words()


def test_get_anagrams_of_a_word():

    # to trigger event handlers (on-startup / on-shutdown)
    # have to use TestClient with a with statement
    # https://fastapi.tiangolo.com/advanced/testing-events/
    with TestClient(app) as client_:

        # testing a default case
        word = 'read'
        response = client_.get(f'/anagrams/{word}.json')
        anagrams_true = ['ared', 'daer', 'dare', 'dear']
        assert response.status_code == 200
        assert all(anagram in response.json()['anagrams'] for anagram in anagrams_true)

        # testing a noun case
        word = 'Read'
        anagrams_true = ['Raed', 'Rade']
        _ = client_.post('/words.json', json={'words': anagrams_true})
        response = client_.get(f'/anagrams/{word}.json?respect_proper_noun=true')
        assert response.status_code == 200
        assert all(anagram in response.json()['anagrams'] for anagram in anagrams_true)

        # testing limit
        word = 'read'
        response = client_.get(f'/anagrams/{word}.json?limit=2')
        assert response.status_code == 200
        assert len(response.json()['anagrams']) == 2


def test_get_storage_stats():
    default_stat_keys = ['count', 'min', 'max', 'median', 'average']
    response = client.get('/words/stats.json')
    assert response.status_code == 200

    # assert that all stats are there
    assert all([key in response.json().keys() for key in default_stat_keys])
    assert all([value > 0 for value in response.json().values()])


def test_are_words_anagrams():

    with TestClient(app) as client_:

        # positive case
        words = ['read', 'ared', 'daer', 'dare', 'dear']
        response = client_.post('/words/are_words_anagrams.json', json={'words': words})
        assert response.status_code == 200
        assert response.json()

        # negative case
        words = ['read', 'ared', 'daer', 'dare', 'AAA']
        response = client_.post('/words/are_words_anagrams.json', json={'words': words})
        assert response.status_code == 200
        assert not response.json()


def test_delete_word_and_anagrams():

    with TestClient(app) as client_:

        word = 'read'
        response = client_.delete(f'/words/delete_word_and_its_anagrams/{word}.json')
        assert response.status_code == 200

        response = client_.get(f'/anagrams/{word}.json')
        assert not response.json()['anagrams']


def test_get_largest_anagram_groups():
    pass


def test_get_anagram_groups_of_size():
    pass
