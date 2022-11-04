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
    - Endpoint to return all anagram groups of size >= x
    - Endpoint to delete a word and all of its anagrams

Issues:
    - storage data structure: plain words in a list VS trie VS improved trie.
    - the trie begs to be coded as a class. Not doing it so it is easy to debug and experiment.
    - global storage not tied to proper db (how do you create / test one?)
    - stats when storage is empty
"""

from fastapi import FastAPI, HTTPException
from utils import (
    get_anagrams,
    add_to_trie,
    trie_to_list_of_lengths,
    delete_word_from_trie,
    anagram_groups_generator,
)

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

# --------- #
# main tasks


@app.post('/words.json', status_code=201)
def add_words(words: dict) -> None:
    app.storage = add_to_trie(trie=app.storage, words=words['words'])


@app.delete('/words/{word}.json', status_code=204)
def delete_word(word: str) -> None:
    # this will not properly delete the word (!)
    # modifies the trie inplace
    delete_word_from_trie(trie=app.storage, word=word)


@app.delete('/words.json', status_code=204)
def delete_all_words() -> None:
    app.storage = {}


@app.get('/anagrams/{word}.json')
def get_anagrams_of_a_word(word: str, limit: int | None = None, respect_proper_noun: bool = False) -> dict:

    anagrams = get_anagrams(
        word=word,
        root=app.storage,
    )

    # note: a word is not considered to be its own anagram
    if word in anagrams:
        anagrams.remove(word)

    if limit:
        anagrams = anagrams[:limit]

    # this is a quick fix that needs to be improved
    # this assumes that only the first letter can be caps
    if respect_proper_noun and anagrams and word[0].isupper():
        anagrams = [word_ for word_ in anagrams if word[0] == word_[0]]

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
def get_largest_anagram_groups() -> dict:
    anagrams = []
    last_size = 0
    for group in anagram_groups_generator(app.storage):
        group_size = len(group)
        if group_size > last_size:
            anagrams = [list(group)]
            last_size = group_size
        elif group_size == last_size:
            anagrams.append(list(group))
    return {'groups': anagrams}


@app.get('/words/anagram_groups_of_size.json')
def get_anagram_groups_of_size(size: int) -> dict:
    anagrams = []
    for group in anagram_groups_generator(app.storage):
        if len(group) == size:
            anagrams.append(list(group))
    return {'groups': anagrams}


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
    trie = add_to_trie({}, words)
    word = words[0]
    anagrams = get_anagrams(word, root=trie)
    if len(anagrams) == len(words):
        return True
    else:
        return False


@app.delete('/words/delete_word_and_its_anagrams/{word}.json')
def delete_word_and_anagrams(word: str) -> None:
    anagrams = get_anagrams_of_a_word(word=word)['anagrams']
    words_to_delete_from_storage = [word] + anagrams
    for word_ in words_to_delete_from_storage:
        delete_word(word_)
