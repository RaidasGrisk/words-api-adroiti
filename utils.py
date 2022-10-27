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


def add_to_trie(trie: dict, words: list[str]) -> dict:
    for word in words:
        this_dict = trie
        for letter in word:
            this_dict = this_dict.setdefault(letter, {})
        this_dict[None] = None
    return trie


# used to debug /test only?
def create_default_trie(filename: str = 'dictionary.txt') -> dict:
    with open(filename) as f:
        words = f.read().splitlines()
    return add_to_trie({}, words)


# recursively yield anagrams
def get_anagrams(
        char_counts: dict,
        path: list,
        root: dict,
        word_length: int,
        respect_proper_noun: bool = False
) -> str:

    # None marks the end of a word, not including this
    # would yield partial anagrams, i.e. word - words
    if None in root and len(path) == word_length:
        yield ''.join(path)

    # loop over each node, i.e
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


# used to debug only?
def trie_to_list_of_words(root: dict) -> list[str]:
    words = []
    for char, root_ in root.items():
        if root_ is None:
            words.append('')
        else:
            for rest in trie_to_list_of_words(root_):
                words.append(char + rest)
    return words


# used fot stats only?
def trie_to_list_of_lengths(root: dict) -> list[int]:
    length = 0
    lengths = []
    for char, root_ in root.items():
        if root_ is None:
            lengths.append(length)
        else:
            length += 1
            for rest in trie_to_list_of_lengths(root_):
                lengths.append(length + rest)
        length = 0
    return lengths


def delete_word_from_trie(trie: dict, word: str) -> None:
    # https://stackoverflow.com/a/15709596/4233305
    # this does not trim the trie only removes the end marker (!)
    # proper implementation should include trie pruning
    # also modifying the trie inplace (!)
    root_ = trie
    for char in word:
        root_ = root_.get(char, None)
        if root_ is None:
            raise Exception('word not in trie')
    # if this point is reached, we're at the end of
    # the word in a trie. Remove the {None: None} marker.
    if None in root_:
        root_.pop(None)


# used to debug /test only?
def is_word_in_trie(trie: dict, word: str) -> bool:
    root_ = trie
    for char in word:
        root_ = root_.get(char, None)
        if root_ is None:
            return False
    # end of the word
    if None in root_:
        return True
    # this can only hit if word is
    # deleted but trie is not pruned
    else:
        return False


# helper to help figure things out manually
def debug_and_test():

    trie = add_to_trie({}, ['Foo', 'Faa', 'Baza', 'Bar', 'Barr'])
    trie = create_default_trie()
    lengths = trie_to_list_of_lengths(trie)
    words = trie_to_list_of_words(trie)
    delete_word_from_trie(trie, 'Bar')
    is_word_in_trie(trie, 'Bar')
