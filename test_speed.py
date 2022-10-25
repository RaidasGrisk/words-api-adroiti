from fastapi.testclient import TestClient
from main import app
import timeit

client = TestClient(app)

perf = timeit.repeat(lambda: client.get("/anagrams/Read.json"), number=100)
print(f'{round(perf[0], 4)}s')
