FROM python:3.8

RUN pip install pipenv

WORKDIR /app
COPY Pipfile* /app/

RUN pipenv install --system

COPY . /app/

# 1 scrape
WORKDIR /app/movie_scrape
RUN START_URL="http://www.imdb.com/search/title?groups=top_1000&sort=user_rating,desc&page=1&ref" ./scrap.sh

# 2 Calculate recommendations
WORKDIR /app
RUN python -m textblob.download_corpora
RUN python -m nltk.downloader stopwords
RUN python tfidf_lsa.py
RUN python doc2vec.py

# 3 Serve server
CMD python server.py

