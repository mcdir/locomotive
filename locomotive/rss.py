
import nltk
import re
import string
import locomotive
from bs4 import BeautifulSoup

# This class is dependent upon the feedparser library, as the "feed" object
# passed to the constructor is a class in that library.

class RssFeed:

    def __init__(self, feed, num, stop_words):
        self.feed = feed
        self.feed_number = num
        self.stop_words = stop_words
        self.url = ''
        self.title = ''
        self.description = ''
        self.items = []
        self.collect()

    def collect(self):
        items_list = self.feed['items']
        for (i, item_obj) in enumerate(items_list):
            # Create a generic hash so that we don't have to pass a feedparser lib "item"
            # object to the constructor of class RssItem.
            generic_hash = {}
            generic_hash['feed_number'] = self.feed_number
            generic_hash['feed_url']    = self.feed['url']
            generic_hash['feed_title']  = self.feed['channel']['title']
            generic_hash['feed_desc']   = self.feed['channel']['description']
            generic_hash['item_number'] = i + 1
            if item_obj.has_key('title'):
                generic_hash['title'] = item_obj['title']
            if item_obj.has_key('tags'):
                generic_hash['tags'] = item_obj['tags']
            if item_obj.has_key('author'):
                generic_hash['author'] = item_obj['author']
            if item_obj.has_key('summary'):
                generic_hash['summary'] = item_obj['summary']
            ri = locomotive.rss.RssItem(generic_hash, self.stop_words)
            self.items.append(ri)


# This class is NOT dependent upon the feedparser library; it is intentionally a generic
# datastructure.  It may be populated from a RssFeed (above class), from database contents,
# or from simulated content such as the nltk news article data.

class RssItem:

    regex = re.compile('[%s]' % re.escape(string.punctuation))

    def __init__(self, generic_hash, stop_words):
        self.feed_url    = ''
        self.feed_number = 0
        self.feed_title  = ''
        self.feed_desc   = ''
        self.item_number = 0
        self.stop_words  = stop_words
        self.author      = ''
        self.title       = ''
        self.category    = 'UNCAT'
        self.categories  = []
        self.tags        = []
        self.all_words   = []
        self.metadata    = ''
        self.guess       = ''

        if generic_hash.has_key('feed_url'):
            self.feed_url = generic_hash['feed_url']

        if generic_hash.has_key('feed_number'):
            self.feed_number = generic_hash['feed_number']

        if generic_hash.has_key('feed_title'):
            words = self.normalized_words(generic_hash['feed_title'])
            self.feed_title = (' '.join(words)).strip()
            self.add_words(self.feed_title)

        if generic_hash.has_key('feed_desc'):
            words = self.normalized_words(generic_hash['feed_desc'])
            self.feed_desc = (' '.join(words)).strip()
            self.add_words(self.feed_desc)

        if generic_hash.has_key('item_number'):
            self.item_number = generic_hash['item_number']

        if generic_hash.has_key('title'):
            words = self.normalized_words(generic_hash['title'])
            self.title = (' '.join(words)).strip()
            self.add_words(self.title)

        if generic_hash.has_key('tags'):
            tags = generic_hash['tags']
            for t in tags: # t is a feedparser.FeedParserDict
                if t.has_key('term'):
                    term  = t['term']
                    words = self.normalized_words(term)
                    for w in words:
                        if self.stop_words.has_key(w):
                            pass
                        else:
                            self.tags.append(w)
                            self.all_words.append(w)

        if generic_hash.has_key('author'):
            words = self.normalized_words(generic_hash['author'])
            self.author = (' '.join(words)).strip()
            self.add_words(self.author)

        if generic_hash.has_key('summary'):
            self.add_words(generic_hash['summary'])

        if generic_hash.has_key('category'):
            self.category = generic_hash['category']

        if generic_hash.has_key('categories'):
            concat_value = generic_hash['categories']
            self.categories = concat_value.split()

        if generic_hash.has_key('metadata'):
            self.metadata = generic_hash['metadata'].strip()

    def pkl_filename(self):
        return 'feed_%d_item_%d.pkl' % (self.feed_number, self.item_number)

    def lookup_key(self):
        return '%04d_%04d' % (self.feed_number, self.item_number)

    def in_category(self, cat):
        return cat in self.categories

    def normalized_words(self, s):
        words = []
        oneline = s.replace('\n', ' ')
        soup = BeautifulSoup(s, "lxml")
        cleaned = soup.get_text(oneline.strip())
        toks1 = cleaned.split()
        for t1 in toks1:
            translated = self.regex.sub('', t1)
            toks2 = translated.split()
            for t2 in toks2:
                t2s = t2.strip()
                if len(t2s) > 1:
                    words.append(t2s.lower())
        return words

    def add_words(self, s):
        words = self.normalized_words(s)
        for w in words:
            if self.stop_words.has_key(w):
                pass
            else:
                self.all_words.append(w)

    def word_count(self):
        return len(self.all_words)

    def word_freq_dist(self):
        freqs = nltk.FreqDist()  # class nltk.probability.FreqDist
        for w in self.all_words:
            #freqs.inc(w, 1)
            freqs[w] += 1
        return freqs

    def features(self, top_words):
        word_set = set(self.all_words)
        features = {}
        features['feed_url'] = self.feed_url
        for w in top_words:
            features["w_%s" % w] = (w in word_set)
        return features

    def normalized_frequency_power(self, word, freqs, largest_count):
        n = self.normalized_frequency_value(word, freqs, largest_count)
        return pow(n, 2)

    def normalized_frequency_value(self, word, freqs, largest_count):
        count = freqs.get(word)
        n = 0
        if count is None:
            n = float(0)
        else:
            n = ((float(count) * float(largest_count)) / float(freqs.N())) * 100.0
        return n

    def normalized_boolean_value(self, word, freqs, largest_count):
        count = freqs.get(word)
        if count is None:
            return float(0)
        else:
            return float(1)

    def knn_data(self, top_words):
        data_array = []
        freqs = self.word_freq_dist()
        largest_count = freqs.values()[0]
        features = {}
        features['feed_url'] = self.feed_url
        for w in top_words:
            data_array.append(self.normalized_boolean_value(w, freqs, largest_count))
        print "knn_data: %s" % data_array
        return data_array

    def in_category(self, cat):
        return cat in self.categories

    def joined_categories(self):
        return ' '.join(self.categories)

    def as_debug_array(self, guess):
        l = []
        l.append('---')
        #l.append('lookup_key:   %s' % (self.lookup_key()))
        l.append('category:     %s' % (self.category))
        l.append('categories:   %s' % (self.joined_categories()))
        l.append('guess:        %s' % (guess))
        l.append('feed_url:     %s' % (self.feed_url))
        l.append('feed_title:   %s' % (self.feed_title))
        l.append('feed_desc:    %s' % (self.feed_desc))
        l.append('author:       %s' % (self.author))
        l.append('title:        %s' % (self.title))
        l.append('tags:         %s' % (' '.join(self.tags)).strip())
        l.append('')
        l.append('all words, by count')
        freqs = nltk.FreqDist([w.lower() for w in self.all_words])
        for w in freqs.keys():
            l.append("%-20s  %d" % (w, freqs.get(w)))
        l.append('')
        l.append('all_words, sequentially:')
        for w in self.all_words:
            l.append(w)
        return l
