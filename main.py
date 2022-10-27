"""
Main tasks:
    - add word to storage
    - get anagrams
    - delete word
    - delete all storage

Optional tasks:
    - get stats
    - Respect a query param for whether or not to include proper nouns in the list of anagrams
    - TODO: Endpoint that identifies words with the most anagrams
    - Endpoint that takes a set of words and returns whether or not they are all anagrams of each other
    - Endpoint to return all anagram groups of size >= x
    - Endpoint to delete a word and all of its anagrams

Issues:
    - storage data structure: plain words in a list VS a trie.
    - should implement a trie class and track word lengths (no need to traverse whole tree after adding a new word)
    Not doing it so it is easy to debug and experiment
    - global storage not tied to proper db (how do you create / test one?)
    - when adding words to the storage, do we check if it is already there? (does not apply for trie)
    - stats when storage is empty
"""

from typing import Union
from fastapi import FastAPI, HTTPException
from utils import get_anagrams, add_to_trie, trie_to_list_of_words, trie_to_list_of_lengths, delete_word_from_trie

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
    filename = 'json/dictionary.json'
    with open(filename) as f:
        words = f.read().splitlines()
    app.storage = add_to_trie({}, words)

# --------- #
# main tasks


@app.post('/words.json', status_code=201)
def add_words(words: dict) -> None:
    app.storage = add_to_trie(trie=app.storage, words=words['words'])


@app.delete('/words/{word}.json', status_code=204)
def delete_word(word: str) -> None:
    # this will not properly delete the word (!)
    delete_word_from_trie(trie=app.storage, word=word)


@app.delete('/words.json', status_code=204)
def delete_all_words() -> None:
    app.storage = {}


@app.get('/anagrams/{word}.json')
def get_anagrams_of_a_word(word: str, limit: Union[int, None] = None, respect_proper_noun: bool = False) -> dict:

    # make sure the proper noun param is accounted for
    # do this here, or inside get_anagrams?
    if not respect_proper_noun:
        word = word.lower()

    # lots of prep work (!), because get_anagrams is recursive,
    # and we don't want to repeat all this inside recursive fn,
    # better just do it all once before recursion, even though
    # it looks like an overkill: i.e. passing char_counts and word_length
    count = 0
    anagrams = []
    char_counts = {char: word.count(char) for char in set(word)}
    args = {
        'char_counts': char_counts,
        'path': [],
        'root': app.storage,
        'word_length': len(word),
        'respect_proper_noun': respect_proper_noun
    }
    for word_ in get_anagrams(**args):
        # note: a word is not considered to be its own anagram
        if word_ != word:
            anagrams.append(word_)
            count += 1

        # early exit if limit is specified
        if limit is not None and limit == count:
            return {'anagrams': anagrams}

    return {'anagrams': anagrams}


# --------- #
# optional tasks


@app.get('/words/stats.json')
def get_storage_stats() -> dict:
    word_lengths = trie_to_list_of_lengths(app.storage)
    return {
        'count': len(word_lengths),
        'min': min(word_lengths),
        'max': max(word_lengths),
        'median': median(word_lengths),
        'average': sum(word_lengths) / len(word_lengths)
    }


@app.get('/words/words_with_most_anagrams.json')
def get_anagram_groups_of_size(size: int) -> dict:

    # hm, this works, rather fast...?
    # there's def a way to do this much faster recursively
    words = trie_to_list_of_words(app.storage)
    word_sets = {}
    for word in words:
        key = tuple(sorted(word))
        word_sets[key] = word_sets.get(key, []) + [word]

    # limit to size
    # better sort or just loop over and del if len(key) < size ?
    sorted_keys = sorted(word_sets, key=lambda k: len(word_sets[k]), reverse=True)
    word_sets_ = [word_sets[key] for key in sorted_keys[:size]]

    return {'groups': word_sets_}


@app.post('/words/are_words_anagrams.json')
def are_words_anagrams(words: dict) -> bool:

    # so because all input has to be proper json
    # can not input just a list, has to be a dict
    words = words.get('words', [])

    # small edge case if a list is empty
    if not words:
        raise HTTPException(
            status_code=422,
            detail='Provided list is empty'
        )

    # if words length is not the same, no point for moving on
    # clever way to check if all len's are the same
    # https://stackoverflow.com/a/35791116/4233305
    words_iter = iter(words)
    length = len(next(words_iter))
    if not all(len(word) == length for word in words_iter):
        return False

    # to check this, don't need to check all combinations.
    # if a single word is an anagram of all words,
    # all words are anagrams of each other
    # so let's just pick the first words and check if
    # it is an anagram of the rest

    # could refactor this, because it pretty
    # much repeats get_anagrams_of_a_word
    trie = add_to_trie({}, words)
    word = words[0]
    char_counts = {char: word.count(char) for char in set(word)}
    args = {
        'char_counts': char_counts,
        'path': [],
        'root': trie,
        'word_length': len(word),
        'respect_proper_noun': False
    }
    anagrams = [word_ for word_ in get_anagrams(**args)]
    if len(anagrams) == len(words):
        return True
    else:
        return False


@app.delete('/words/delete_word_and_its_anagrams/{word}.json')
def delete_word_and_anagrams(word: str) -> None:
    anagrams = get_anagrams_of_a_word(word)['anagrams']
    words_to_delete_from_storage = [word] + anagrams
    for word_ in words_to_delete_from_storage:
        delete_word(word_)
