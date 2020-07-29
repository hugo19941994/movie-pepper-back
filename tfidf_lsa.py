#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Calculate tf-idf and lsa vectors for each movie
Extract keywords
Save the results to the corresponding JSON for offline processing
"""

import json
import string
import io
from typing import Any, List
from concurrent.futures import ProcessPoolExecutor

from collections import defaultdict
from langdetect import detect  # type: ignore
from langdetect.lang_detect_exception import LangDetectException  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from nltk.stem.snowball import SnowballStemmer  # type: ignore
from nltk.tokenize import TabTokenizer  # type: ignore
from nltk.wsd import lesk  # type: ignore
from sklearn.decomposition import TruncatedSVD  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.pipeline import make_pipeline  # type: ignore
from sklearn.preprocessing import Normalizer  # type: ignore
from textblob import TextBlob  # type: ignore


def _get_best_keyword(key: str, originals: dict) -> str:
    word = ''
    best = 0

    # TODO: Best keywords can be pre-computed, we shouldn't do this every
    # iteration

    # originals.json contains keys of lemmatized words and values of original
    # words. These words are associated with their number of occurences in the
    # downloaded texts. Get the original word which is more common
    for keyword in originals[key].items():
        if keyword[1] > best:
            word = keyword[0]

    return word


def _check_exists(key: str, item: dict) -> bool:
    return key in item and \
        item[key] is not None and \
        item[key] != ''


# TODO: Delete these entries?
def _check_english(text: str) -> bool:
    try:
        if detect(text) == 'en':
            return True
        return False
    except LangDetectException as exception:
        return False
    except Exception as exception:
        print(exception)
        return False


def _load_list(json_list: List[dict]) -> List[str]:
    """Load the names of the movies and the corpus"""
    # Original synopsis
    corpus: List[str] = []

    with open('./movie_scrape/imdb.json', 'r') as in_file:
        for item in json.load(in_file):
            if _check_exists('plot', item) and \
                    _check_english(item['plot']):
                revs = ''.join(item['reviews'])
                corpus.append(item['plot'] + revs)
                json_list.append(item)

    return corpus


def repl(text):
    tokenizer = TabTokenizer()
    mod_text = ""
    for sentence in text.split("."):
        sentence = sentence.strip()
        blob = TextBlob(sentence, tokenizer=tokenizer)
        tags = blob.pos_tags
        for j in tags:
            if j[1] == 'NNP':  # Delete proper nouns
                sentence = sentence.replace(j[0], "")
            if j[1] == 'NN' or j[1] == 'NNS':
                synset = lesk(sentence.split(), j[0])
                if synset is not None:
                    if len(synset.hypernyms()) > 0:
                        syn = synset.hypernyms()[0].name().split(".")[0]
                        sentence = sentence.replace(j[0], syn)
        mod_text += sentence + " "
    return mod_text


# TODO: Comprobar arbol synset
def _replace_with_hypernym(corpus: list) -> list:
    """
    Replace nouns with the hypernym of the most appropriate synset
    using lesk. Delete any proper nouns such as names
    """

    corpus_0 = []
    with ProcessPoolExecutor() as executor:
        for mod_text in executor.map(repl, corpus):
            corpus_0.append(mod_text)

    return corpus_0


def _represents_int(num_str: str) -> bool:
    """Check if a string is a number"""
    try:
        int(num_str)
        return True
    except ValueError:
        return False


def filt(text):
    """Remove stopwords from a string"""
    filtered_text = ""
    for word in text.split():
        # TODO Don't check if every word is an int
        if word not in stopwords.words('english') and \
                not _represents_int(word):
            filtered_text += word + " "
    return filtered_text


def _filter_stopwords(corpus_0: list) -> list:
    """Delete any english stopwords"""

    corpus_1 = []  # Synopsis without stopwords
    with ProcessPoolExecutor() as executor:
        for filtered_text in executor.map(filt, corpus_0):
            corpus_1.append(filtered_text)

    return corpus_1


def stemm(text):
    stemmer = SnowballStemmer("english")
    stemmed_text = ""
    for word in text.split():

        # Remove punctuation
        # Fastest according to
        # http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
        table = str.maketrans({key: None for key in string.punctuation})
        word = word.translate(table)

        stemmed_word = stemmer.stem(word)

        if stemmed_word != "" or stemmed_word != " ":
            #originals[stemmed_word][word] += 1
            stemmed_text += stemmed_word + " "

    return stemmed_text


def _stemm_synopsis(corpus_1: list, originals: dict) -> list:
    """Stemm all possible words"""

    corpus_2 = []

    with ProcessPoolExecutor() as executor:
        for stemmed_text in executor.map(stemm, corpus_1):
            corpus_2.append(stemmed_text)

    return corpus_2


def _filter_text(json_list: list) -> list:
    """Text treatment"""
    print("Filtering Text")

    corpus = _load_list(json_list)

    # Synsets
    corpus_0 = _replace_with_hypernym(corpus)

    # Stemming text
    corpus_1 = _filter_stopwords(corpus_0)

    # Stemmed synopsis
    '''Save a dictionary with original lemmatized
    words and a list of their originals'''
    originals: defaultdict = defaultdict(lambda: defaultdict(int))
    corpus_2 = _stemm_synopsis(corpus_1, originals)
    # with open('./originals.json', 'w') as out_file:  # Overwrite file!
    # json.dump(originals, out_file, indent=2)

    return corpus_2


def _movie_distance(lsa_matrix: dict, json_list: list) -> None:
    """Calculate cosine similairty"""
    print("Calulating LSA")

    for i, _ in enumerate(lsa_matrix):
        json_list[i]['lsa'] = lsa_matrix[i].tolist()


def _get_keywords(json_list: list, tfidf_x: dict,
                  vectorizer: TfidfVectorizer) -> None:
    """Calculate tf-idf vector and extract keywords"""
    print("Calculating TFIDF and extracting keywords")

    for i, item in enumerate(json_list):
        item['tf-idf'] = tfidf_x[i].tolist()
        indices = sorted(
            range(len(tfidf_x[i])),
            key=lambda x, idx=i: tfidf_x[idx][x], reverse=True
        )
        item['p_keywords'] = []
        for loop, j in enumerate(indices):
            if tfidf_x[i][j] != 0 and loop < 50:
                item['p_keywords'].append(vectorizer.get_feature_names()[j])
                # print(vectorizer.get_feature_names()[j])
            else:
                break


def _save_files(json_list: list) -> None:
    """Dump JSONs to files"""
    t = []
    for item in json_list:
        '''
        restored_keywords = []
        with open('./originals.json') as in_file:
            originals = json.load(in_file)
            for keyword in item['keywords']:
                restored_keywords.append(
                _get_best_keyword(keyword, originals))
                '''

        t.append({'tf-idf': item['tf-idf'],
                  'lsa': item['lsa'],
                  'keywords': item['p_keywords'],
                  'imdb_keywords': item['keywords'],
                  'title': item['title'],
                  'director': item['director'],
                  'year': item['year'],
                  'rating': item['rating'],
                  'genres': item['genres'],
                  'plot': item['plot'],
                  'reviews': item['reviews'],
                  'url': item['url'],
                  'poster': item['poster']})

    with io.open('./db.json', 'w', encoding='utf8') as out_file:
        json.dump(t, out_file, indent=4, ensure_ascii=False)


def calculate_corpus_var(max_df: int = 200,
                         min_df: int = 5,
                         n_components: int = 1000,
                         max_features: Any = None) -> None:

    """
    tf-idf parameters:
        max_df - Remove items that appear too frequently
        min_df - Remove items that are too specific
        int -> more/less than int number of documents
        float -> more/less than the float percentage of documents
    """

    json_list: list = []
    corpus = _filter_text(json_list)

    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', strip_accents='unicode',
                                 max_df=max_df, min_df=min_df,
                                 max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    tfidf_array = tfidf_matrix.toarray()
    _get_keywords(json_list, tfidf_array, vectorizer)

    # LSA
    svd = TruncatedSVD(n_components=n_components)
    normalizer = Normalizer(copy=False)
    lsa = make_pipeline(svd, normalizer)
    lsa_matrix = lsa.fit_transform(tfidf_matrix)

    _movie_distance(lsa_matrix, json_list)

    _save_files(json_list)


if __name__ == "__main__":
    calculate_corpus_var()
