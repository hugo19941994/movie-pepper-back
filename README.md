# Movie Pepper Backend

[![license](https://img.shields.io/github/license/hugo19941994/movie-pepper-back.svg)](https://github.com/hugo19941994/movie-pepper-back/blob/master/LICENSE.md)
[![Requirements Status](https://requires.io/github/hugo19941994/movie-pepper-back/requirements.svg?branch=master)](https://requires.io/github/hugo19941994/movie-pepper-back/requirements/?branch=master)

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
```

## Crawler

A Bash script is provided to simplify executing the Spidy crawler.

```bash
cd movie_scrape
START_URL="http://www.imdb.com/search/title?groups=top_1000&sort=user_rating,desc&page=1&ref" ./scrap.sh
```

After the crawl is complete calculate the TF-IDF values.

```bash
python tfidf_lsa.py
```

This step is needed to execute the server.

## Server

Start the server

```bash
python server.py
```

You will probably want to use a reverse proxy such as NGINX and secure it with HTTPS.
