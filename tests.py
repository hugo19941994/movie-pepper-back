from tfidf_lsa import calculate_corpus_var
import json
import os
import shutil
import subprocess
import unittest

class TestMoviePepper(unittest.TestCase):

    def test_crawl(self):
        try:
            shutil.rmtree('./movie_scrape/crawls')
            os.remove('./movie_scrape/imdb.json')
            os.remove('./db.json')
        except FileNotFoundError:
            pass
        except OSError:
            pass

        subprocess.run(['START_URL="http://www.imdb.com/search/title?role=nm0000095&title_type=feature&user_rating=8.0,10" ./scrap.sh'], cwd="./movie_scrape/", shell=True)

        try:
            with open('./movie_scrape/imdb.json', 'r') as in_file:
                json.load(in_file)
        except:
            self.fail()

    def test_tfidf_lsa(self):
        calculate_corpus_var(max_df=200, min_df=2, n_components=10, max_features=None)

        try:
            with open('./db.json', 'r') as in_file:
                json.load(in_file)
        except:
            self.fail()

if __name__ == '__main__':
    unittest.main()
