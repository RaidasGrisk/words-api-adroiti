from fastapi.testclient import TestClient
from main import app
from utils import create_default_trie, get_anagrams
import timeit

client = TestClient(app)

perf = timeit.repeat(lambda: client.get("/anagrams/Read.json"), number=100)
print(f'{round(perf[0], 4)}s')


# -------- #
# test and debug if this works fine
trie = create_default_trie()


def debug_get_anagrams(word: str, limit: None | int = None, respect_proper_noun: bool = False) -> list[str]:

    # make sure the proper noun param is accounted for
    if not respect_proper_noun:
        word = word.lower()

    # get char dict
    char_counts = {char: word.count(char) for char in set(word)}

    count = 0
    anagrams = []
    for word_ in get_anagrams(
            char_counts=char_counts,
            path=[],
            root=trie,
            word_length=len(word),
            respect_proper_noun=respect_proper_noun
    ):
        # from the task description:
        # Note that a word is not considered to be its own anagram.
        if word_ != word:
            anagrams.append(word_)

        # early exit if limit is specified
        if limit is not None and limit == count:
            return anagrams

    return anagrams


perf = timeit.repeat(lambda: debug_get_anagrams(word='Read'), number=100)
print(f'{round(perf[0], 4)}s')