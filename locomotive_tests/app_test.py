import os
import unittest
import sys
import time 
import locomotive

class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = locomotive.app.Application()
        
    def tearDown(self):
        pass 
        
    def test_redis_url(self):
        url = self.app.redis_url() 
        self.assertEqual(url, 'redis://localhost:6379/')

    def test_development_feeds_list(self):
        feeds_list = self.app.development_feeds_list() 
        self.assertTrue(len(feeds_list) == 14)
        self.assertTrue('feed://news.yahoo.com/rss/stock-markets' in feeds_list) 
        self.assertFalse('https://locomotivellc.campfirenow.com/' in feeds_list)

    def test_locomotive_feeds_list(self):
        feeds_list = self.app.locomotive_feeds_list() 
        self.assertTrue(len(feeds_list) == 8)
        self.assertTrue('http://www.thesportsphysiotherapist.com/feed/' in feeds_list) 
        self.assertFalse('https://locomotivellc.campfirenow.com/' in feeds_list)

    def test_load_training_categories(self):
        categories = self.app.load_training_categories() 
        self.assertTrue(len(categories) > 100)
        self.assertTrue(len(categories) < 300)
        self.assertTrue(categories['0001_0001'] == 'UNCAT')

    def test_stop_words(self):
        stop_words = self.app.stop_words()
        self.assertTrue(len(stop_words) >= 127)
        self.assertTrue(stop_words['and'] == 0)
        if stop_words.has_key('locomotive'): 
            self.fail('locomotive should not be a stop word')

    def test_write_data_file(self):
        line  = "test data file generated on %d" % (time.time())
        lines = [line]
        filename = self.app.write_data_file('unittest_datafile.txt', lines)
        self.assertTrue(filename == 'data/unittest_datafile.txt')
        f = open(filename, 'r')
        input_lines = f.readlines()
        f.close() 
        self.assertTrue(input_lines[0].strip() == line)

    def test_write_output_file(self):
        line  = "test output file generated on %d" % (time.time())
        lines = [line]
        filename = self.app.write_output_file('unittest_outputfile.txt', lines)
        self.assertTrue(filename == 'output/unittest_outputfile.txt')
        f = open(filename, 'r')
        input_lines = f.readlines()
        f.close() 
        self.assertTrue(input_lines[0].strip() == line) 
