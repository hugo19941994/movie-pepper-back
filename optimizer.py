import numpy as np
import matplotlib.pyplot as plt
from recommender import Recommender
from itertools import product


rec = Recommender()

objective = {
    "The Godfather": [
        "The Godfather: Part II",
        "The Godfather: Part III",
        "The Shawshank Redemption",
        "Scarface"
    ]
}

x = [0, 1, 2, 3]
my_xticks = ['The Godfather: Part II', 'The Godfather: Part II',
             'The Shawshank Redemption', 'Scarface']

director_v = [1, 3, 5]
genres_v = [1, 3, 5]
imdb_keywords_v = [1, 3, 5]
lsa_v = [1, 5, 10]

film_quantity = rec.film_quantity()

counter = 0
results = []
labels = []
for director, genres, imdb_keyword, lsa in product(director_v,
                                                   genres_v,
                                                   imdb_keywords_v,
                                                   lsa_v):
    ratio = {'director': director,
             'genres': genres,
             'imdb_keywords': imdb_keyword,
             'lsa': lsa}

    res = rec.recommend("The Godfather", ratio, film_quantity)
    movs = [x['title'] for x in res]
    tot = 0
    s2 = []
    for mov in objective['The Godfather']:
        s2.append(movs.index(mov))
        tot += movs.index(mov)
    labels.append(tot)
    results.append(s2)
    print(ratio)
    print(tot)

cmap = plt.get_cmap('jet')
colors = cmap(np.linspace(0, 1, len(results)))

plt.xticks(x, my_xticks)
for idx, (res, color, tot) in enumerate(zip(results, colors, labels)):
    plt.plot(x, res, color=color, label=tot)
plt.legend(loc='best')
plt.show()
