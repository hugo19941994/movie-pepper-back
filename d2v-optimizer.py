import numpy as np
from textwrap import shorten
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib2tikz import save as tikz_save
from recommender import Recommender
from itertools import product
from doc2vec import doc2vec_model


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


def get_cmap(n, name='jet'):
    return plt.cm.get_cmap(name, n)


def rand_jitter(arr):
    stdev = .01*(max(arr)-min(arr))
    return arr + np.random.randn(len(arr)) * stdev


def calculate(movie):
    size_v = [1000]
    window_v = [5]
    min_count_v = [5]
    iter_v = [5, 10, 20, 50]

    # Enumerate movies
    x = [x for x, y in enumerate(objective[movie])]
    my_xticks = objective[movie]  # labels in x axis

    d2v_variations = product(size_v, window_v, min_count_v, iter_v)

    i = 0
    results = []
    labels = []
    plt.ylabel("Posición de la recomendación")
    plt.xlabel("Películas")

    for size, window, min_count, ite in d2v_variations:
        i += 1
        # Train a new model
        d2v = doc2vec_model()
        d2v.create_model(size, window, min_count, ite)
        rec = Recommender()
        film_quantity = rec.film_quantity()
        res = d2v.recommendation(movie, film_quantity)

        movs = [r[0] for r in res]  # all recommendations
        # tot = 0
        scores = []
        for mov in objective[movie]:
            try:
                scores.append(movs.index(mov))  # append to scores the movie score
                # tot += movs.index(mov)
            except Exception as e:
                print(e)
                scores.append(0)  # Movie not found!

        results.append(scores)
        print(scores)

        label_template = "size {} window {} minc {} iter {} tot {}"
        label = label_template.format(size, window, min_count, ite,
                                      sum(scores))
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

    # Truncate longer titles to 12 characters
    my_xticks = [
        shorten(z, width=15, placeholder=".")
        for (y, z)
        in sorted(zip(totals, my_xticks),
                  key=lambda pair: pair[0])
    ]

    plt.xticks(x, my_xticks, rotation=45)

    cmap = get_cmap(i)  # Number of variations
    print(rand_jitter(x))
    print(x)
    print(labels)
    print(results)
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

