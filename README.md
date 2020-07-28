# Movie Pepper Backend

[![Build Status](https://travis-ci.com/hugo19941994/movie-pepper-back.svg?branch=master)](https://travis-ci.com/hugo19941994/movie-pepper-back)
[![Coverage Status](https://coveralls.io/repos/github/hugo19941994/movie-pepper-back/badge.svg?branch=master)](https://coveralls.io/github/hugo19941994/movie-pepper-back?branch=master)

This repo contains all the backend code for the Movie Pepper open source recommendation engine.

This includes the REST API and the [IMDb](www.imdb.com) crawler.

## Setup

Python 3, pip and virtualenv must be installed

Create a virtualenv

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
python -m nltk.downloader stopwords
```

## Crawler

A Bash script is provided to simplify executing the Spidy crawler.

```bash
cd movie_scrape
START_URL="http://www.imdb.com/search/title?groups=top_1000&sort=user_rating,desc&page=1&ref" ./scrap.sh
```

After the crawl is complete calculate the TF-IDF values and Doc2Vec models.

```bash
python tfidf_lsa.py
python doc2vec.py
```

This step is needed to execute the server.

## Server

Start the server

```bash
python server.py
```

You will probably want to use a reverse proxy such as NGINX and secure it with HTTPS.
