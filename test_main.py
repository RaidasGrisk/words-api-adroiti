from fastapi.testclient import TestClient
from main import app
from utils import get_storage

client = TestClient(app)


def test_add_words():

    # populate the storage by adding all words
    storage = get_storage()
    response = client.post('/words.json', json={'words': storage})
    assert response.status_code == 200
    assert len(client.app.storage) > 0  # == 235886


def test_delete_word():

    word = 'dummy_word'

    # populate the storage with single word
    response = client.post('/words.json', json={'words': [word]})
    assert response.status_code == 200
    assert word in client.app.storage

    # delete the word
    response = client.delete(f'/words/{word}.json')
    assert response.status_code == 200
    assert word not in client.app.storage


def test_delete_all_words():
    response = client.delete('/words.json')
    assert response.status_code == 200
    assert len(client.app.storage) == 0

    test_add_words()


def test_get_anagrams_of_a_word():

    # testing a default case
    word = 'read'
    response = client.get(f'/anagrams/{word}.json')
    assert response.json() == {"anagrams": ["ared", "daer", "dare", "dear"]}

    # testing a noun case
    word = 'Read'
    _ = client.post('/words.json', json={'words': ['deaR', 'daRe']})
    response = client.get(f'/anagrams/{word}.json?respect_proper_noun=true')
    assert response.json() == {'anagrams': ['deaR', 'daRe']}


def test_get_storage_stats():
    default_stat_keys = ['count', 'min', 'max', 'median', 'average']
    response = client.get('/words/stats.json')
    assert response.status_code == 200

    # assert that all stats are there
    assert all([key in response.json().keys() for key in default_stat_keys])
    assert all([value > 0 for value in response.json().values()])
