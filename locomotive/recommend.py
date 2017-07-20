
import codecs
import locale
import nltk
from   numpy import *
import operator
import os
import pickle
import random
import sys

import locomotive

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

class Recommend:

    def __init__(self, application):
        self.app = application

    def recommend_categories_by_cats(self):
        self.metadata   = self.read_reuters_metadata()
        self.stop_words = self.app.stop_words()
        self.all_words  = []
        self.rss_items  = self.read_training_articles(self.metadata, 999999, self.stop_words)
        self.category_array = self.collect_unique_categories_by_freq()
        self.cat_assoc = locomotive.category_associations.CategoryAssociations(self.category_array)
        self.display_categories()

        self.labels, self.profiles, self.info = self.collect_items_data()
        self.dataset = array(self.profiles)

        for (i, prof) in enumerate(self.profiles):
            print "%s %d %s %s" % (prof, i, self.labels[i], self.info[i])

        for (i, prof) in enumerate(self.profiles):
            cat1 = self.labels[i]
            info = self.info[i]
            results = self.knn_classify(prof, self.dataset, self.labels, 10)
            print "cat1: %-10s  result is %s for case %d, %s" % (cat1, results, i, info)
            for tup in results:
                cat2 = tup[0]; count = tup[1]
                if cat1 != cat2:
                    self.cat_assoc.increment(cat1, cat2, count)
                    self.cat_assoc.increment(cat2, cat1, count)

        for (i, cat) in enumerate(self.category_array):
            assoc = self.cat_assoc.associations(cat)
            print "assoc for cat: %-10s %s" % (cat, assoc)

    def read_reuters_metadata(self):
        cats_file = "%s%s" % (self.app.reuters_metadata_dir(), 'cats.txt')
        print cats_file
        f = open(cats_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_training_articles(self, metadata, max_count, stop_words):
        rss_items = []
        for (i, line) in enumerate(metadata):
            if i <= max_count:
                a = locomotive.news.NewsArticle(self.app.reuters_metadata_dir(), line, stop_words)
                rss_items.append(a.as_rss_item())
        print "%d articles/items have been read" % (len(rss_items))
        return rss_items

    def collect_unique_categories_by_freq(self):
        freqs = nltk.FreqDist()
        sorted_cats = []
        for item in self.rss_items:
            for w in item.categories:
                #freqs.inc(w, 1)
                freqs[w] += 1
        for cat in freqs.keys():
            sorted_cats.append(cat)
            print "collect_sorted_categories: %s  %d" % (cat, freqs.get(cat))
        return sorted_cats

    def identify_top_words(self, all_words):
        freq_dist = nltk.FreqDist(w.lower() for w in all_words)
        top_words = freq_dist.keys()[:1000]
        self.app.write_output_file('words_top.txt', top_words)
        return top_words

    def display_categories(self):
        for (i, cat) in enumerate(self.category_array):
            print "category_index %d = %s" % (i, cat)

    def collect_items_data(self):
        labels = []; profiles = []; items_info = []
        for item in self.rss_items:
            profile = []
            for cat in self.category_array:
              if item.in_category(cat):
                  profile.append(float(1.0))
              else:
                  profile.append(float(0.0))
            profiles.append(profile)
            labels.append(item.category)
            items_info.append("%s %s" % (item.feed_title, item.joined_categories()))
        return labels, profiles, items_info

    def knn_classify(self, inX, dataSet, labels, k):
        dataSetSize = dataSet.shape[0]
        diffMat     = tile(inX, (dataSetSize, 1)) - dataSet
        sqDiffMat   = diffMat ** 2
        sqDistances = sqDiffMat.sum(axis = 1)
        distances   = sqDistances ** 0.5
        classCount  = {}
        sortedDistIndicies = distances.argsort()
        for i in range(k):
            voteIlabel = labels[sortedDistIndicies[i]]
            if classCount.has_key(voteIlabel):
                classCount[voteIlabel] += 1
            else:
                classCount[voteIlabel] = 1
        sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
        # Return an array of one or more tuples like this:
        # [('interest', 4), ('earn', 2), ('money-fx', 2), ('dlr', 1), ('yen', 1)]
        return sortedClassCount

    def knn_simple(self):
        print "knn_simple categorization example:"
        dataset, labels = self.create_simple_dataset()
        print "dataset:\n%s" % (str(dataset))
        print "labels: %s" % (str(labels))
        test_cases = []
        test_cases.append([0.1,0.1,0.6])
        test_cases.append([0.5,0.5,0.6])
        test_cases.append([0.6,0.6,0.6])
        test_cases.append([0.9,0.9,0.6])
        for tc in test_cases:
            result = self.knn_klassify(tc, dataset, labels, 3)
            print "result is %s for case %s , type: %s" % (result, str(tc), str(type(tc)))

    def create_simple_dataset(self):
        group  = array([[1.0,1.1,0.5],[1.0,1.0, 0.5],[0.0,0.0,0.5],[0.0,0.1,0.5]])
        labels = ['A','A','B','B']
        return group, labels

    def knn_klassify(self, inX, dataSet, labels, k):
        dataSetSize = dataSet.shape[0]
        diffMat     = tile(inX, (dataSetSize, 1)) - dataSet
        sqDiffMat   = diffMat ** 2
        sqDistances = sqDiffMat.sum(axis = 1)
        distances   = sqDistances ** 0.5
        classCount  = {}
        sortedDistIndicies = distances.argsort()
        for i in range(k):
            voteIlabel = labels[sortedDistIndicies[i]]
            if classCount.has_key(voteIlabel):
                classCount[voteIlabel] += 1
            else:
                classCount[voteIlabel] = 1
        sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
        print sortedClassCount
        return sortedClassCount[0][0]

    def collect_all_words(self, articles):
        words = []
        freqs = nltk.FreqDist()
        for a in articles:
            for w in a.all_words:
                words.append(w)
                #freqs.inc(w, 1)
                freqs[w] += 1

        print('collect_all_words count: ' + str(len(words)))
        self.app.write_output_file('words_all.txt', words)

        l = []
        for w in freqs.keys():
            l.append("%-30s  %d" % (w, freqs.get(w)))
        self.app.write_output_file('words_all_freq.txt', l)

        return words