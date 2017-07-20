
import codecs
import feedparser
import httplib
import locale
import pickle
import sys
from   urlparse import urlparse

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

class Capture:

    def __init__(self, application):
        self.app = application
        self.data_dir = self.app.data_directory()
        feeds_list = self.app.development_feeds_list()
        for (i, url) in enumerate(feeds_list):
            print('---')
            self.capture_as_pickled_feed(url, i + 1)
            self.capture_as_xml(url, i + 1)

    def save_responses(self):
        return True

    def capture_as_pickled_feed(self, url, feed_number):
        feed = feedparser.parse(url)
        filename = self.data_dir + 'feed_' + str(feed_number) + '.pkl'
        if self.save_responses():
            print('Capture.capture_as_pickled_feed - saving feed %d to file %s from url %s' % (feed_number, filename, url))
            f = open(filename,'w')
            pickle.dump(feed, f)
            f.close()
        else:
            print 'Capture.capture_as_pickled_feed - save_responses is disabled'

    def capture_as_xml(self, url, feed_number):
        parsed = urlparse(url)
        conn = httplib.HTTPConnection(parsed.netloc)
        conn.request("GET", parsed.path)
        resp = conn.getresponse()
        if self.save_responses():
            print "Capture.capture_as_xml - %s %s %s , %d lines" % (resp.status, resp.reason, url, feed_number)
            basename = 'feed_' + str(feed_number) + '.xml'
            content  = resp.read()
            ucontent = self.app.to_unicode(content)
            lines    = ucontent.splitlines()
            self.app.write_data_file(basename, lines)
        else:
            print 'Capture.capture_as_xml - save_responses is disabled'
