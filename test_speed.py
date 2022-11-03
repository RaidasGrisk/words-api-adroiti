from fastapi.testclient import TestClient
from main import app
from utils import create_default_trie, get_anagrams
import timeit

client = TestClient(app)
trie = create_default_trie()

perf = timeit.repeat(lambda: get_anagrams('read', trie), number=100)
print(f'{round(perf[0], 4)}s')