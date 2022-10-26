"""
Source: # https://scipython.com/blog/finding-anagrams-with-a-trie/

What is a trie?
https://drstearns.github.io/tutorials/trie/

words = [Foo, Faa, Baz, Bar]
trie = {
    'F': {
        'o': {
            'o': {None: None}
        },
        'a': {
            'a', {None: None}
        }
    },
    'B': {
        'a': {
            'z': {None: None},
            'r': {None: None}
        }
    }
}
"""


def add_to_trie(trie, words):
    # how the heck does this work?
    # the output is clear, but having
    # trouble understanding how does this work
    for word in words:
        this_dict = trie
        for letter in word:
            this_dict = this_dict.setdefault(letter, {})
        this_dict[None] = None
    return trie


# this is not used anywhere, except for tests and debug
def create_default_trie(filename: str = 'dictionary.txt') -> dict:
    with open(filename) as f:
        words = f.read().splitlines()
    return add_to_trie({}, words[:5])


# recursive function
def get_anagrams(char_counts: dict, path: list, root: dict, word_length: int, respect_proper_noun: bool = False):

    # None marks the end of a word, not including this
    # would yield partial anagrams, i.e. word - words
    if None in root and len(path) == word_length:
        yield ''.join(path)

    # loop over each node, i.e
    # root_ = {'A': {None: None}, 'a': {None: None, 'a': {None: None, 'l': {None: None, 'i': {'i': {None: None}}}}}}
    # char | root_ :
    # A | {None: None}
    # a | {None: None, 'a': {None: None, 'l': {None: None, 'i': {'i': {None: None}}}}}
    for char, root_ in root.items():

        # make sure the proper noun param is accounted for
        if char and not respect_proper_noun:
            char = char.lower()

        count = char_counts.get(char, 0)

        # check if node char is in our word
        # if not, move on with the next node
        if count == 0:
            continue

        # if node char is in our word
        # increment -1 and save the char to path
        char_counts[char] = count - 1
        path.append(char)

        # here's the tricky part (!)
        # pass the current root_ further deep into the recursion stack
        # and see if it yields something.
        for word_ in get_anagrams(char_counts, path, root_, word_length, respect_proper_noun):
            yield word_

        # this too is very tricky (!)
        # clean up the stack after the yield
        # so for this char, reset path and char_counts
        # what happens if we get rid of this - nothing,
        # except that memory use goes up?
        path.pop()
        char_counts[char] = count


def trie_to_list_of_words(root):
    words = []
    for char, root_ in root.items():
        if root_ is None:
            words.append('')
        else:
            for rest in trie_to_list_of_words(root_):
                words.append(char + rest)
    return words


def trie_to_list_of_lengths(root):
    length = 0
    lengths = []
    for char, root_ in root.items():
        if root_ is None:
            lengths.append(length)
            length = 0
        else:
            for rest in trie_to_list_of_lengths(root_):
                length += 1
                lengths.append(length + rest)
    return lengths


# test and debug if this works fine
def debug_get_anagrams(word: str, limit: None | int = None, respect_proper_noun: bool = False) -> list[str]:

    trie = create_default_trie()
    lengths = trie_to_list_of_lengths(trie)
    words = trie_to_list_of_words(trie)

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
