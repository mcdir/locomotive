import logging
import os
import unittest
import sys
import locomotive


class RssItemTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(stream=sys.stdout)
        logging.getLogger("RssItemTest").setLevel(logging.DEBUG)

        self.app = locomotive.app.Application()
        self.stop_words = self.app.stop_words()
        basedir = self.app.reuters_metadata_dir()
        metadata = 'training/10043 ship iron-steel'
        article = locomotive.news.NewsArticle(basedir, metadata, self.stop_words)
        self.item = article.as_rss_item()

    def tearDown(self):
        pass

    def test_categories(self):
        cats = self.item.categories
        # self.log(self.item.categories)
        self.assertTrue(len(cats) == 2)
        self.assertTrue(cats[0] == 'ship')
        self.assertTrue(cats[1] == 'iron-steel')

    def test_in_category(self):
        self.assertTrue(self.item.in_category('ship'))
        self.assertTrue(self.item.in_category('iron-steel'))
        self.assertFalse(self.item.in_category('tebow'))

    def test_joined_categories(self):
        self.assertTrue(self.item.joined_categories() == 'ship iron-steel')
        self.assertFalse(self.item.joined_categories() == 'tebow iron-steel')

    def test_no_stop_words(self):
        for w in self.item.all_words:
            if self.stop_words.has_key(w):
                self.fail('item contains a stop word - ' + w)

    def log(self, msg):
        log = logging.getLogger("RssItemTest")
        log.debug(str(msg))


'''
cat cats.txt | grep 10043 => training/10043 ship iron-steel

Contents of file training/10043:

REPORT EXPECTS SHARP DROP IN WORLD IRON IMPORTS
  World seaborne iron ore imports will
  fall sharply by the year 2000 with declining imports to the EC
  and Japan only partially offset by increased demand from South
  East Asia, a report by Ocean Shipping Consultants said.
      The report predicts annual world seaborne iron ore imports
  of 267.7 mln tonnes by 2000 versus 312.4 mln tonnes in 1985.
      It estimates that total bulk shipping demand from the iron
  ore sector will fall by almost 10 pct, or 200 billion tonne
  miles, with shipping demand associated with the coking trade
  down about 17 pct or 130 billion tonne miles.
      The report sees EC imports falling to 91.7 mln tonnes in
  2000 from 123.6 mln in 1985 with Japanese imports falling to 89
  mln from 124.6 mln tonnes. Imports to South East Asia are seen
  rising to 58.6 mln from 32.6 mln tonnes in 1985.
      It predicts that EC steel production will fall to 109 mln
  tonnes in 2000 from 135.7 mln in 1985 with Japanese production
  falling to 92 mln from 105.3 mln.
      South Korea and Taiwan are expected to double their output
  to 40 mln tonnes with Chinese production increasing by 25 mln
  tonnes to 80 mln, it added.

'''
