import codecs
import locale
import nltk
import sys
import os
import urlparse

import locomotive

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


class Application:
    def __init__(self):
        self.args = sys.argv

    def capture(self):
        locomotive.capture.Capture(self)

    def classify(self):
        c = locomotive.classify.Classify(self)
        c.classify()

    def gen_cat_file(self):
        c = locomotive.classify.Classify(self)
        c.generate_training_category_file()

    def load_training_categories(self):
        categories = {}
        f = open(self.data_directory() + 'training_categories.txt', 'r')
        input_lines = f.readlines()
        for line in input_lines:
            tokens = line.split('|')
            if len(tokens) > 2:
                key = tokens[0].strip()
                val = tokens[1].strip()
                categories[key] = val
        print('%d categories loaded from text file' % (len(categories)))
        return categories

    def knn_simple(self):
        c = locomotive.classify.Classify(self)
        c.knn_simple()

    def knn_rss(self):
        c = locomotive.classify.Classify(self)
        c.knn_rss()

    def knn_reuters(self):
        c = locomotive.classify.Classify(self)
        c.knn_reuters()

    def classify_reuters(self):
        c = locomotive.classify.Classify(self)
        c.classify_reuters()

    def recommend_categories_by_cats(self):
        r = locomotive.recommend.Recommend(self)
        r.recommend_categories_by_cats()

    def development_feeds_list(self):
        heredoc = """
        http://rss.cnn.com/rss/edition.rss
        http://rss.cnn.com/rss/edition_europe.rss   
        https://www.yahoo.com/news/rss/stock-markets
        https://www.yahoo.com/news/rss/energy
        https://www.yahoo.com/news/rss/health
        http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml
        http://www.espn.com/espn/rss/news
        """
        return self.parse_feed_list(heredoc)

    def locomotive_feeds_list(self):
        heredoc = """
        https://www.yahoo.com/news/rss/stock-markets
        https://www.yahoo.com/news/rss/energy
        https://www.yahoo.com/news/rss/health
        http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml
        http://www.espn.com/espn/rss/news
        """
        return self.parse_feed_list(heredoc)

    def stop_words(self):
        word_hash = {}
        words_list = nltk.corpus.stopwords.words('english')  # 127 words
        for w in words_list:
            word_hash[w] = 0
            str = 'stopword: %s' % (w)
            print(str)
        return word_hash

    def parse_feed_list(self, heredoc):
        flist = []
        lines = heredoc.splitlines()
        for line in lines:
            l = line.strip()
            if len(l) > 0:
                flist.append(l)
        return flist

    def redis_url(self):
        if os.environ.get('REDISTOGO_URL'):
            return os.environ.get('REDISTOGO_URL')
        else:
            return 'redis://localhost:6379/'

    def redis_connect(self):
        url = self.redis_url()
        url = urlparse.urlparse(url)
        # return redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)

    def is_ascii(self, s):
        if s.__class__.__name__ == 'str':
            return True
        return False

    def to_unicode(self, s):
        if self.is_ascii(s):
            return unicode(s, 'utf-8')
        else:
            return s

    def reuters_metadata_dir(self):
        return os.path.expanduser('~/nltk_data/corpora/reuters/')

    def data_directory(self):
        return 'data/'

    def output_directory(self):
        return 'output/'

    def log(self, obj):
        print(str(obj))

    def write_data_file(self, basename, lines):
        filename = self.data_directory() + basename
        print('Application.write_file: ' + filename + '  ' + str(len(lines)) + ' lines')
        f = codecs.open(filename, 'w', 'utf-8')
        for line in lines:
            f.write(line)
            f.write('\n')
        f.close
        return filename

    def write_output_file(self, basename, lines):
        filename = self.output_directory() + basename
        print('Application.write_output_file: ' + filename + '  ' + str(len(lines)) + ' lines')
        f = codecs.open(filename, 'w', 'utf-8')
        for line in lines:
            f.write(line)
            f.write('\n')
        f.close
        return filename
