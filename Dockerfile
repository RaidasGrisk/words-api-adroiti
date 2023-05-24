# docker build -t eu.gcr.io/small-services-no-project/words-api-adroiti -f Dockerfile .
# docker run -p 8080:8080 eu.gcr.io/small-services-no-project/words-api-adroiti
# docker push eu.gcr.io/small-services-no-project/words-api-adroiti
# gcloud run deploy --image eu.gcr.io/small-services-no-project/words-api-adroiti --port 8080

FROM python:3.10
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY main.py /code
COPY utils.py /code
COPY dictionary.txt /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
