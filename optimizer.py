import numpy as np
from textwrap import shorten
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib2tikz import save as tikz_save
from recommender import Recommender
from itertools import product
from tfidf_lsa import calculate_corpus_var


class defaultlist(list):
    """List returning default value when accessing uninitialized index.

    Original implementation: http://stackoverflow.com/a/8719940/315168
    """

    def __init__(self, fx):
        self._fx = fx

    def __setitem__(self, index, value):
        while len(self) <= index:
            self.append(self._fx())
        list.__setitem__(self, index, value)

    def __getitem__(self, index):
        """Allows self.dlist[0] style access before value is initialized."""
        while len(self) <= index:
            self.append(self._fx())
        return list.__getitem__(self, index)


def calculate_variation(movie, director, genres, imdb_keyword, lsa, rec):
    film_quantity = rec.film_quantity()

    ratio = {'director': director,
             'genres': genres,
             'imdb_keywords': imdb_keyword,
             'lsa': lsa}

    res = rec.recommend(movie, ratio, film_quantity)

    movs = [r['title'] for r in res]  # all recommendations
    # tot = 0
    scores = []
    for mov in objective[movie]:
        try:
            scores.append(movs.index(mov))  # append to scores the movie score
            # tot += movs.index(mov)
        except Exception as e:
            print(e)
            scores.append(0)  # Movie not found!

    return scores


def get_cmap(n, name='jet'):
    return plt.cm.get_cmap(name, n)


def rand_jitter(arr):
    stdev = .01*(max(arr)-min(arr))
    return arr + np.random.randn(len(arr)) * stdev


def calculate(movie):
    """
    max_df_v = [50]
    min_df_v = [5]
    max_features_v = [None]  # TF-IDF features
    n_components_v = [1000]  # LSA components
    """
    max_df_v = [100]
    min_df_v = [2, 5, 10, 25]
    max_features_v = [None]  # TF-IDF features
    n_components_v = [1000]  # LSA components

    director_v = [0]
    genres_v = [0]
    imdb_keywords_v = [0]
    lsa_v = [1]

    # Enumerate movies
    x = [x for x, y in enumerate(objective[movie])]
    my_xticks = objective[movie]  # labels in x axis

    tfidf_lsa_variations = product(max_df_v, min_df_v,
                                   n_components_v, max_features_v)

    i = 0
    results = []
    labels = []
    plt.ylabel("Posición de la recomendación")
    plt.xlabel("Películas")

    for max_df, min_df, n_components, max_features in tfidf_lsa_variations:
        # Train a new model
        calculate_corpus_var(max_df, min_df, n_components, max_features)
        rec = Recommender()

        movie_weights = product(director_v, genres_v, imdb_keywords_v, lsa_v)
        for director, genres, imdb_keywords, lsa in movie_weights:
            if lsa == 0 and imdb_keywords == 0:
                continue
            if imdb_keywords == 0 and lsa == 6:
                continue
            if imdb_keywords == 0 and lsa == 12:
                continue
            i += 1
            # Iterate weight combinations

            result = calculate_variation(movie, director, genres,
                                         imdb_keywords, lsa, rec)
            results.append(result)
            print(result)
            label_template = "feat {} cmpn {} mndf {} mxdf {} keyw {}\% lsa {}\% tot {}"
            try:
                ratiop = int((imdb_keywords/(imdb_keywords + lsa)) * 100)
            except Exception:
                ratiop = 0.0
            label = label_template.format(max_features, n_components,
                                          min_df, max_df, ratiop,
                                          100 - ratiop, sum(result))
            labels.append(label)
            print(label)

    # sort results and labels accordingly:
    totals = defaultlist(int)
    for result in results:
        for idx, score in enumerate(result):
            totals[idx] += score
    print(totals)

    for idx, result in enumerate(results):
        results[idx] = [z for (y, z) in sorted(zip(totals, result),
                                               key=lambda pair: pair[0])]
    print(results)

    # Tuncate longer titles to 12 characters
    my_xticks = [
        shorten(z, width=15, placeholder=".")
        for (y, z)
        in sorted(zip(totals, my_xticks),
                  key=lambda pair: pair[0])
    ]

    plt.xticks(x, my_xticks, rotation=45)

    cmap = get_cmap(i)  # Number of variations
    for idx, (result, label) in enumerate(zip(results, labels)):
        plt.scatter(rand_jitter(x), result, color=cmap(idx), label=label)
        fit = np.polyfit(x, result, deg=1)
        plt.plot(np.unique(x), np.poly1d(fit)(np.unique(x)),
                 color=cmap(idx), alpha=0.5)

    # Save figure and clean - One chart per film with all variations
    plt.gca().set_ylim(bottom=0)

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(loc='best', prop=fontP)

    tikz_save("./{}.tex".format(''.join(movie)),
              figureheight='\\figureheight',
              figurewidth='\\figurewidth')
    plt.clf()  # Clean figure


if __name__ == '__main__':
    """
    """

    objective = {
        "2001: A Space Odyssey": [
            "Alien",
            "Distrito 9",
            "Interstellar",
            "Solaris",
            "The Martian",
            "Gravity",
            "Planet of the Apes"
        ],
        "Apocalypse Now": [
            "Platoon",
            "Full Metal Jacket",
            "Paths of Glory",
            "Saving Private Ryan",
            "The Deer Hunter"
        ],
        "Ratatouille": [
            "The Incredibles",
            "Toy Story 2",
            "Monsters, Inc.",
            "Shrek",
            "Ponyo",
            "My Neighbor Totoro"
        ]
    }

    for movie in objective.keys():
        calculate(movie)
