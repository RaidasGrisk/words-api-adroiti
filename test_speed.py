from fastapi.testclient import TestClient
from main import app
from utils import get_storage, is_anagram
import timeit

client = TestClient(app)
storage = get_storage()


def debug_get_anagrams(word: str, limit: None | int = None, respect_proper_noun: bool = False) -> list[str]:
    anagrams = []
    count = 0
    for storage_word in storage:
        if is_anagram(storage_word, word, respect_proper_noun):
            anagrams.append(storage_word)
            count += 1
        # early exit if limit is specified
        if limit is not None and limit == count:
            return anagrams
    return anagrams


perf = timeit.repeat(lambda: debug_get_anagrams(word='Read'), number=100)
print(f'{round(perf[0], 4)}s')
