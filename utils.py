"""
Source: # https://scipython.com/blog/finding-anagrams-with-a-trie/

What is a trie?
https://drstearns.github.io/tutorials/trie/
https://www.cs.usfca.edu/~galles/visualization/Trie.html
"""


def add_to_trie(trie: dict, words: list[str]) -> dict:
    for word in words:
        word_sorted = tuple(sorted(word.lower()))
        root = trie
        for letter in word_sorted:
            root = root.setdefault(letter, {})
        # set None to a set and add the word to it
        # does this inplace, so no assignment
        root.setdefault(None, set()).add(word)
    return trie


# used to debug / test only?
def create_default_trie(filename: str = 'dictionary.txt') -> dict:
    with open(filename) as f:
        words = f.read().splitlines()
    return add_to_trie({}, words)


def get_anagrams(word: str, root: dict) -> list[str]:

    # prep work
    word_sorted = tuple(sorted(word.lower()))
    root_ = root
    anagrams = []

    for char in word_sorted:
        if char in root_:
            root_ = root_[char]

    # by now, we are at the end of provided word
    # check if None in root_ and return
    if None in root_:
        anagrams = list(root_[None])

    return anagrams


# used to debug only
def trie_to_list_of_words(root: dict) -> list[str]:
    lengths = []
    for _, root_ in root.items():
        if None in root_:
            lengths += root_[None]
        if isinstance(root_, dict):
            lengths += trie_to_list_of_words(root_)
    return lengths


# used for stats only
def trie_to_list_of_lengths(root: dict) -> list[int]:
    lengths = []
    for _, root_ in root.items():
        if None in root_:
            lengths += [len(word) for word in root_[None]]
        if isinstance(root_, dict):
            lengths += trie_to_list_of_lengths(root_)
    return lengths


def delete_word_from_trie(trie: dict, word: str) -> None:
    # this does not trim the trie only removes the word from saved words
    # proper implementation should include trie pruning
    root_ = trie
    word_sorted = tuple(sorted(word.lower()))
    for char in word_sorted:
        if char in root_:
            root_ = root_[char]
        else:
            raise Exception('word not in trie')
    if word in root_[None]:
        root_[None].remove(word)


# used to debug /test only?
def is_word_in_trie(trie: dict, word: str) -> bool:
    root_ = trie
    word_sorted = tuple(sorted(word.lower()))
    for char in word_sorted:
        root_ = root_.get(char, None)
        if root_ is None:
            return False
    # end of the word
    if None in root_ and word in root_[None]:
        return True
    # this can only hit if word is
    # deleted but trie is not pruned
    else:
        return False


def anagram_groups_generator(root: dict) -> set:
    for _, root_ in root.items():
        if isinstance(root_, dict):
            for group in anagram_groups_generator(root_):
                yield group
    if None in root:
        yield root[None]


def prune_trie(trie: dict) -> None:
    # TODO: have to backtrack and delete child if it has no leafs
    root = trie
    for _, root_ in root.items():
        if isinstance(root_, dict):
            prune_trie(root_)
        if None in root_ and not root_[None]:
            del root_[None]


# helper to help figure things out manually
def debug_and_test():

    trie = add_to_trie({}, ['Foo', 'oof', 'Faa', 'Baza', 'Bar', 'Barr'])
    trie = create_default_trie()
    get_anagrams('read', trie)
    lengths = trie_to_list_of_lengths(trie)
    words = trie_to_list_of_words(trie)
    delete_word_from_trie(trie, 'Bar')
    is_word_in_trie(trie, 'Bar')

    [print(group) for group in anagram_groups_generator(trie)]
