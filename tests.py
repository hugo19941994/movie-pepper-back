from tfidf_lsa import calculate_corpus_var, _check_english
from doc2vec import doc2vec_model
import brotli
import json
import os
import shutil
import subprocess
import unittest

class TestMoviePepper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clean old files if needed
        try:
            shutil.rmtree('./movie_scrape/crawls')
            os.remove('./movie_scrape/imdb.json')
            os.remove('./db.json')
            os.remove('./my_model.doc2vec')
        except FileNotFoundError:
            pass
        except OSError:
            pass

        # Download dataset
        subprocess.run(['START_URL="http://www.imdb.com/search/title?role=nm0000095&title_type=feature&user_rating=8.0,10" ./scrap.sh'], cwd="./movie_scrape/", shell=True)

        # Create TF-IDF and LSA model
        calculate_corpus_var(max_df=200, min_df=2, n_components=10, max_features=None)

        # Create Doc2Vec model
        d2v = doc2vec_model()
        d2v.main()

    def test_crawl(self):
        try:
            with open('./movie_scrape/imdb.json', 'r') as in_file:
                json.load(in_file)
        except:
            self.fail()

    def test_tfidf_lsa(self):
        try:
            with open('./db.json', 'r') as in_file:
                json.load(in_file)
        except:
            self.fail()

    def test_create_d2v(self):
        if not os.path.isfile('./my_model.doc2vec'):
            self.fail()

    def test_server_movies(self):
        import server
        self.app = server.app.test_client()
        resp = self.app.get("/movies")
        movs = brotli.decompress(resp.get_data())
        self.assertEqual(resp.status_code, 200)
        try:
            json.loads(movs)
        except:
            self.fail()

    def test_server_recommend(self):
        import server
        self.app = server.app.test_client()
        resp = self.app.get("/recommend/Annie%20Hall")
        movs = brotli.decompress(resp.get_data())
        self.assertEqual(resp.status_code, 200)
        try:
            json.loads(movs)
        except:
            self.fail()

    def test_server_d2vrecommend(self):
        import server
        self.app = server.app.test_client()
        resp = self.app.get("/recommend-d2v/Annie%20Hall")
        movs = brotli.decompress(resp.get_data())
        self.assertEqual(resp.status_code, 200)
        try:
            json.loads(movs)
        except:
            self.fail()

    def test_env(self):
        self.assertEqual(_check_english("Hello my name is Hugo"), True)
        self.assertEqual(_check_english("Hola mi nombre es Hugo"), False)
        self.assertEqual(_check_english("ugobsdo47h ogy ro83g 34or8g r838f4qf9gyg7fwer"), False)
        self.assertEqual(_check_english(42.0), False)

    @classmethod
    def tearDownClass(cls):
        # Clean old files if needed
        try:
            shutil.rmtree('./movie_scrape/crawls')
            os.remove('./movie_scrape/imdb.json')
            os.remove('./db.json')
            os.remove('./my_model.doc2vec')
        except FileNotFoundError:
            pass
        except OSError:
            pass

if __name__ == '__main__':
    unittest.main()
