# Movie Pepper Backend

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

## Server

Start the server

```bash
python server.py
```

You will probably want to use a reverse proxy such as NGINX and secure it with HTTPS.

## Crawler

A Bash script is provided to simplify executing the Spidy crawler.

```bash
./movie_scrape/scrap.sh
```

