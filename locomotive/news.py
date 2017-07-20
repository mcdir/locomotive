
import nltk
import re
import string
import locomotive
from bs4 import BeautifulSoup

# This class is created to read a Reuters News Article from the nltk sample data,
# then cast it as a similated "RssItem".  The reason for this is to leverage the
# large and already categorized reuters data in the nltk library.

class NewsArticle:

    regex = re.compile('[%s]' % re.escape(string.punctuation))

    def __init__(self, basedir, cats_file_metadata, stop_words):
        self.basedir    = basedir
        self.metadata   = cats_file_metadata
        self.stop_words = stop_words
        self.category   = '?'
        self.result     = '?'
        self.categories = []

        tokens = self.metadata.strip().split()  # example: training/14777 money-fx dlr
        for (i, token) in enumerate(tokens):
            if i == 0:
                self.path = token
            elif i == 1:
                self.category = token # primary category
                self.categories.append(token)
            else:
                self.categories.append(token)

        tokens = self.path.strip().split('/')
        self.file_number = tokens[1].strip()
        self.freqs       = nltk.FreqDist()
        self.title_words = []
        self.all_words   = []
        self.guess       = ''
        self.read_input_file()

    def read_input_file(self):
        f = open(self.basedir + self.path, 'r')
        input_lines = f.readlines()
        f.close()
        for (i, line) in enumerate(input_lines):
            line_words  = self.normalized_words(line)
            if i == 0:
                # line 1 contains the news article title, we "boost" these words
                for w in line_words:
                    self.title_words.append(w)
                    #self.freqs.inc(w, 1)
                    self.freqs[w] += 1
            for w in line_words:
                self.all_words.append(w)
                #self.freqs.inc(w, 1)
                self.freqs[w] += 1
                #fd = FreqDist(my_text)

    def normalized_words(self, s):
        words   = []
        oneline = s.replace('\n', ' ').lower()
        soup = BeautifulSoup(s, "lxml")
        cleaned = soup.get_text(oneline.strip())
        toks1   = cleaned.split()
        for t1 in toks1:
            translated = self.regex.sub('', t1)
            toks2 = translated.split()
            for t2 in toks2:
                if len(t2) > 1:
                    if self.stop_words.has_key(t2):
                        pass
                    else:
                        words.append(t2.lower())
        return words

    def joined_categories(self):
        return ' '.join(self.categories)

    # This method exists so that we can produce a large set of simulated RSS Feed Items
    # from the set of Reuters news articles in the nltk dataset.

    def as_rss_item(self):
        generic_hash = {}
        generic_hash['feed_number'] = 0
        generic_hash['feed_url']    = self.metadata
        generic_hash['metadata']    = self.metadata
        generic_hash['feed_title']  = self.path
        generic_hash['feed_desc']   = 'python nltk article data'
        generic_hash['item_number'] = self.file_number
        generic_hash['category']    = self.category
        generic_hash['categories']  = self.joined_categories()
        generic_hash['title']       = ' '.join(self.title_words)
        generic_hash['summary']     = ' '.join(self.all_words)
        return locomotive.rss.RssItem(generic_hash, self.stop_words)
