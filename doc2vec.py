from gensim import models
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import pathlib
import json


class doc2vec_model:
    def __init__(self):
        if pathlib.Path('./my_model.doc2vec').is_file():
            self.model = models.Doc2Vec.load('my_model.doc2vec')
        else:
            self.model = self.create_model()
        return

    def create_model(self, size=1000, window=5, min_count=5, iter=20):
        with open('./db.json', 'r') as in_file:
            movies = json.load(in_file)

        docs = []
        for movie in movies:
            review_comb = ""
            for review in movie['reviews']:
                review_comb += review
            docs.append(TaggedDocument(words=[x.lower() for x
                                               in review_comb.split(" ")],
                                        tags=[movie['title']]))

        self.model = Doc2Vec(docs, vector_size=size, window=window,
                             min_count=min_count, workers=8, epochs=iter)

        self.model.save("my_model.doc2vec")

        return self.model

    def recommendation(self, movie_title, topn=None):
        if topn is None:
            topn = len(self.model.docvecs)
        return self.model.docvecs.most_similar([movie_title],
                                               topn=topn)

    def main(self):
        pass
        #print(self.model.docvecs['The Godfather'])
        #print(self.model.similar_by_word('airplane'))
        #print(self.model.similar_by_word('plant'))
        #print(self.model.similar_by_word('air'))
        #print(self.model.docvecs.most_similar(["The Godfather"],
                                              #topn=len(self.model.docvecs)))


if __name__ == "__main__":
    d2v = doc2vec_model()
    d2v.main()
