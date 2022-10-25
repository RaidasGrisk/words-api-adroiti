"""
Main tasks:
    - add word to storage
    - get anagrams
    - delete word
    - delete all storage

Optional tasks:
    - get stats
    - Respect a query param for whether or not to include proper nouns in the list of anagrams
    - Endpoint that identifies words with the most anagrams
    - Endpoint that takes a set of words and returns whether or not they are all anagrams of each other
    - TODO: Endpoint to return all anagram groups of size >= x
    - Endpoint to delete a word and all of its anagrams

Issues:
    - global storage not tied to proper db (how do you create / test one?)
    - when adding words to the storage, do we check if it is already there?
    - stats when storage is empty
"""

from fastapi import FastAPI, HTTPException
from utils import create_default_trie, get_anagrams, add_to_trie

# python does not have a default median func
from statistics import median

app = FastAPI()

# such storage has drawbacks!
# if multiple nginx workers are spawned
# a different copy is stored in each worker
# will load (populate) this on each startup
app.storage = {}


@app.on_event('startup')
def load_storage():
    filename = 'dictionary.txt'
    with open(filename) as f:
        words = f.read().splitlines()
    app.storage = add_to_trie({}, words)


@app.post('/words.json')
def add_words(words: dict) -> None:
    # what if word is already in the storage?
    # will return multiple copies of the same word
    app.storage = app.storage + words['words']


@app.delete('/words/{word}.json')
def delete_word(word: str) -> None:

    # simply remove the None: None escape
    # this will not properly delete a word
    app.storage.remove(word)


@app.delete('/words.json')
def delete_all_words() -> None:
    app.storage = []


@app.get('/anagrams/{word}.json')
def get_anagrams_of_a_word(
        word: str,
        limit: int | None = None,
        respect_proper_noun: bool = False
) -> dict:

    # make sure the proper noun param is accounted for
    if not respect_proper_noun:
        word = word.lower()

    count = 0
    anagrams = []
    char_counts = {char: word.count(char) for char in set(word)}
    for word_ in get_anagrams(
            char_counts=char_counts,
            path=[],
            root=app.storage,
            word_length=len(word),
            respect_proper_noun=respect_proper_noun
    ):
        # from the task description:
        # Note that a word is not considered to be its own anagram.
        if word_ != word:
            anagrams.append(word_)

        # early exit if limit is specified
        if limit is not None and limit == count:
            return {'anagrams': anagrams}

    return {'anagrams': anagrams}


# --------- #
# optional


@app.get('/words/stats.json')
# Endpoint that returns a count of words in
# the corpus and min/max/median/average word length
def get_storage_stats() -> dict:

    word_lengths = []
    for word in app.storage:
        word_lengths.append(len(word))

    return {
        'count': len(word_lengths),
        'min': min(word_lengths),
        'max': max(word_lengths),
        'median': median(word_lengths),
        'average': sum(word_lengths) / len(word_lengths)
    }


@app.get('/words/words_with_most_anagrams.json')
# Endpoint that returns a count of words in
# the corpus and min/max/median/average word length
def get_words_with_most_anagrams() -> dict:
    counts = {}
    word_count = len(app.storage)
    word_progress = 0
    for base_word in app.storage:

        # check progress
        word_progress += 1
        if word_progress % 2 == 0:
            print(word_progress, 'out of', word_count)

        for word in app.storage:
            if is_anagram(base_word, word):
                counts[base_word] = counts.get(base_word, 0) + 1
    return dict(sorted(counts.items()))


@app.post('/words/are_words_anagrams.json')
# Endpoint that takes a set of words and returns
# whether they are all anagrams of each other
def are_words_anagrams(words: list[str]) -> bool:

    # to check this, don't need to check all combinations
    # if a single word is an anagram of all words
    # it means, all are anagrams of each other
    # so let's just pick the first words and check if
    # it is an anagram of the rest

    # small edge case if a list is empty
    if not words:
        raise HTTPException(
            status_code=422,
            detail='Provided list is empty'
        )

    base_word = words.pop()
    for word in words:
        if not is_anagram(base_word, word):
            return False
    return True


@app.delete('/words/delete_word_and_its_anagrams/{word}.json')
# Endpoint to delete a word and all of its anagrams
def delete_word_and_anagrams(word: str) -> None:
    for word_ in app.storage:
        if is_anagram(word, word_):
            delete_word(word_)
    delete_word(word)
