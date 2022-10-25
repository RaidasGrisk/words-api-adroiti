
def get_storage(filename: str = 'dictionary.txt') -> list[str]:
    with open(filename) as f:
        storage = f.read().splitlines()
    return storage


def is_anagram(word1: str, word2: str, respect_proper_noun: bool = False) -> bool:

    # if different length, already not an anagram
    if len(word1) != len(word2):
        return False

    # proper nouns
    # important: the placement of this check
    # must be at this exact location, this will break
    # it this part is moved elsewhere
    if not respect_proper_noun:
        word1 = word1.lower()
        word2 = word2.lower()

    # from the task description:
    # Note that a word is not considered to be its own anagram.
    if word1 == word2:
        return False

    # check if words has same letters
    # many solutions here, could use:
    # set, sort, loop over each char, trie (this would be fastest)
    char_count = {}

    for char1, char2 in zip(word1, word2):
        char_count[char1] = char_count.get(char1, 0) + 1
        char_count[char2] = char_count.get(char2, 0) - 1

    for char in char_count:
        if char_count[char] != 0:
            return False

    return True

