#!/usr/bin/env python

"""
Sisrec.py
Movies recomendation engine
"""

from typing import List  # noqa: F401
from scipy.spatial.distance import cosine
from concurrent.futures import ProcessPoolExecutor
import sys
import math
import json

# Importance of each column
DEFAULT_RATIO = {'director': 1,
                 'genres': 2,
                 'imdb_keywords': 3,
                 'lsa': 10}


def union(list_a: list, list_b: list) -> list:
    """Return the union of two lists"""
    if list_a is None:
        list_a = [None]
    if list_b is None:
        list_b = [None]
    return list(set(list_a) | set(list_b))


def ordenar(comparacion: dict, length: int = 10) -> dict:
    """Sort the results"""

    # Save 10 films ordered by similarity
    orden_similitud = sorted(comparacion['pels'],
                             key=lambda x: x['similitud'],
                             reverse=True)[:length]

    comparacion['pels'] = orden_similitud
    #print([x['pel']['title'] for x in comparacion['pels']])
    return comparacion


def compare(mov: dict, pel: dict, ratio: dict = None) -> float:
    """Compute similarity between two movies"""

    if ratio is None:
        ratio = DEFAULT_RATIO

    similitudtotal = 0.0

    # Compare each element of each column which has a ratio assigned. For every
    # match the similarity increases. Basically Jaccard index of every column.
    try:
        # LSA compared separately!
        for campo_a, campo_b in [
                (x, y) for x, y
                in zip(mov.items(), pel.items()) if x[0]
                in ratio and x[0] != 'lsa'
        ]:
            total = len(union(campo_a[1], campo_b[1]))
            if total > 0:
                coincidente = len(
                    [(x, y) for x in campo_a[1] for y in campo_b[1] if x == y]
                )
                similitudtotal += (coincidente/total) * ratio[campo_a[0]]

        # Only compare LSA if configured to do so
        if 'lsa' in ratio:
            # LSA is comapred using cosine distance
            syn_similarity = (
                1 - cosine(
                    pel['lsa'],
                    mov['lsa']
                )
            ) * ratio['lsa']
            # Sometimes LSA is not valid and syn_simality = NaN
            if not math.isnan(float(syn_similarity)):
                similitudtotal += syn_similarity

    except Exception:
        return 0.0

    return similitudtotal


def rec(mov: dict, pel: dict, ratio: dict = None) -> dict:
    similitudtotal: float = 0.0

    if ratio is not None:
        similitudtotal = compare(mov, pel, ratio)
    else:
        similitudtotal = compare(mov, pel)

    return {
        "similitud": similitudtotal,
        "pel": pel
    }


class Recommender:
    def __init__(self) -> None:
        print("loading")
        sys.stdout.flush()
        self.peliculas: List[dict] = self.load()

    def get_movies(self):
        r = []
        for pel in self.peliculas:
            r.append(
                {
                    'title': pel['title'],
                    'poster': pel['poster'],
                    'director': pel['director'],
                    'genres': ", ".join(pel['genres']),
                    'year': pel['year'],
                    'rating': pel['rating'],
                    'url': pel['url']
                }
            )
        return r

    def film_quantity(self):
        return len(self.peliculas)

    def recommend(self, movie, ratio=None, film_quantity = 10):
        print(movie)
        mov = None
        for m in self.peliculas:
            if m['title'].replace(u'\u00a0', '') == movie:
                mov = m

        if mov is None:
            return None

        comparacion: list = []
        # Compare mov with all films except itself
        with ProcessPoolExecutor() as executor:
            for pel in [
                    x for x in self.peliculas if x['title'] != mov['title']
            ]:
                if ratio is not None:
                    comparacion.append(executor.submit(rec, mov,
                                                       pel, ratio).result())
                else:
                    comparacion.append(executor.submit(rec, mov,
                                                       pel).result())

        comp = {'mov': mov, 'pels': comparacion}
        r = ordenar(comp, film_quantity)

        return ([x['pel'] for x in r['pels']])

    def ask_movie(self, peliculas: list) -> dict:
        """Select a movie"""

        print("Select a movie")
        print("Press 0 for the complete list")
        print("Press a letter for the movies that start with that letter")

        while True:
            letter: str = input()

            # If the user inputs 0 the complete list
            # of movies and their id's is displayed
            if letter == "0":
                for pel in peliculas:
                    print(pel['title'])
            else:
                # Return first id coincidence
                # None if id is not found
                for pel in peliculas:
                    if pel['title'].replace(u'\u00a0', '') == letter:
                        return pel

    @staticmethod
    def clean(item: list) -> list:
        """Each row is a string. Lists must be separated and stripped"""
        item = [x.replace("'", "")
                .replace('"', '')
                .replace('[', '')
                .replace(']', '')
                .split(',') for x in item]

        return item

    @staticmethod
    def load() -> list:
        """Load every synopsis in a list"""
        peliculas: list = []

        with open('./db.json', 'r') as in_file:
            for film in json.load(in_file):
                peliculas.append(film)

        # Sort films by ID
        # Useful when asking the user to select a movie
        peliculas = sorted(peliculas, key=lambda x: x['title'])
        return peliculas

    def main_loop(self, peliculas: list) -> dict:
        """Main loop"""

        mov: dict = self.ask_movie(peliculas)
        print(mov['title'])

        comparacion: list = []
        # Compare mov with all films except itself
        for pel in [x for x in peliculas if x['title'] != mov['title']]:
            similitudtotal = compare(mov, pel)
            comparacion.append({"similitud": similitudtotal, "pel": pel})

        comp = {'mov': mov, 'pels': comparacion}
        return comp

    @staticmethod
    def get_best_keyword(key: str, originals: dict) -> str:
        word = ''
        best = 0

        # TODO: Best keywords can be pre-computed, we shouldn't do this every
        # iteration

        # originals.json contains keys of lemmatized words and values of
        # original words. These words are associated with their number
        # of occurences in the downloaded texts.
        # Get the original word which is more common
        for keyword in originals[key].items():
            if keyword[1] > best:
                word = keyword[0]

        return word

    def main(self) -> None:
        """Main"""

        while True:
            comparacion: dict = self.main_loop(self.peliculas)
            ordenar(comparacion)


if __name__ == "__main__":
    recommender: Recommender = Recommender()
    recommender.main()
