# Performance tracking

---
`timeit.repeat(lambda: client.get("/anagrams/Read.json"), number=100)`

Find anagrams by:
  - simple dicts of chars: 3.67s
  - trie: ?s
---


Signal Backend Dev Project
=========

# The Project

---

The project is to build an API that allows fast searches for [anagrams](https://en.wikipedia.org/wiki/Anagram). `dictionary.txt` is a text file containing every word in the English dictionary. Ingesting the file doesn’t need to be fast, and you can store as much data in memory as you like.

The API you design should respond on the following endpoints as specified.

- `POST /words.json`: Takes a JSON array of English-language words and adds them to the corpus (data store).
- `GET /anagrams/{word}.json`:
  - Returns a JSON array of English-language words that are anagrams of the word passed in the URL.
  - This endpoint should support an optional query param that indicates the maximum number of results to return.
- `DELETE /words/{word}.json`: Deletes a single word from the data store.
- `DELETE /words.json`: Deletes all contents of the data store.

**Optional**
- Endpoint that returns a count of words in the corpus and min/max/median/average word length
- Respect a query param for whether or not to include proper nouns in the list of anagrams
- Endpoint that identifies words with the most anagrams
- Endpoint that takes a set of words and returns whether or not they are all anagrams of each other
- Endpoint to return all anagram groups of size >= *x*
- Endpoint to delete a word *and all of its anagrams*

Clients will interact with the API over HTTP, and all data sent and received is expected to be in JSON format

Example (assuming the API is being served on localhost port 8000):

```{bash}
# Adding words to the corpus
$ curl -i -X POST -d '{ "words": ["read", "dear", "dare"] }' http://localhost:8000/words.json
HTTP/1.1 201 Created
...

# Fetching anagrams
$ curl -i http://localhost:8000/anagrams/read.json
HTTP/1.1 200 OK
...
{
  anagrams: [
    "dear",
    "dare"
  ]
}

# Specifying maximum number of anagrams
$ curl -i http://localhost:8000/anagrams/read.json?limit=1
HTTP/1.1 200 OK
...
{
  anagrams: [
    "dare"
  ]
}

# Delete single word
$ curl -i -X DELETE http://localhost:8000/words/read.json
HTTP/1.1 204 No Content
...

# Delete all words
$ curl -i -X DELETE http://localhost:8000/words.json
HTTP/1.1 204 No Content
...
```

Note that a word is not considered to be its own anagram.

## Testing

Optionally, you can provide tests that verify the functionality of the API.

The sample dictionary is provided as a baseline for testing real world functionality and performance of the API.

## Documentation

Optionally, you can provide documentation that is useful to consumers and/or maintainers of the API.

Suggestions for documentation topics include:

- Features you think would be useful to add to the API
- Implementation details (which data store you used, etc.)
- Limits on the length of words that can be stored or limits on the number of results that will be returned
- Any edge cases you find while working on the project
- Design overview and trade-offs you considered

# Deliverable
---

Please provide the code for the assignment either in a private repository (GitHub or Bitbucket etc) or as a zip file. If you have a deliverable that is deployed on the web please provide a link, otherwise please provide instructions for running it locally.