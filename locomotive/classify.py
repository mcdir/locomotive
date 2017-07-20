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


class Classify:
    def __init__(self, application):
        self.app = application

    def classify(self):
        categories = self.app.load_training_categories()
        stop_words = self.app.stop_words()
        feed_items = self.load_pickled_feed_items(self.app, categories, stop_words)
        all_words = self.collect_all_words(feed_items)
        top_words = self.identify_top_words(all_words)

        random.shuffle(feed_items)

        featuresets = []
        for item in feed_items:
            item_features = item.features(top_words)
            tup = (item_features, item.category)  # tup is a 2-element tuple
            featuresets.append(tup)

        train_set = featuresets

        print('featuresets count: ' + str(len(featuresets)))

        print("training...")
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        print("training complete")

        if True:
            summary_lines = []
            detail_lines = []
            actual_category_counts = {}
            guessed_category_counts = {}
            correct_category_counts = {}
            wrong_category_counts = {}
            correct_count = 0
            wrong_count = 0
            for item in feed_items:
                df = item.features(top_words)
                if item.lookup_key() in categories:
                    cat = categories[item.lookup_key()]
                else:
                    cat = 'Unknown'
                guess = classifier.classify(df)
                result = 'wrong'
                actual_category_counts[cat] = actual_category_counts.get(cat, 0) + 1
                guessed_category_counts[guess] = guessed_category_counts.get(guess, 0) + 1
                if guess == cat:
                    result = 'correct'
                    correct_count = correct_count + 1
                    correct_category_counts[cat] = correct_category_counts.get(cat, 0) + 1
                else:
                    wrong_count = wrong_count + 1
                    wrong_category_counts[cat] = wrong_category_counts.get(cat, 0) + 1

                line = 'item: %s  actual: %-18s  guess: %-18s  %-8s  %4d  %-s' % (
                    item.lookup_key(), cat, guess, result, item.word_count(), item.title)
                summary_lines.append(self.app.to_unicode(line))
                detail_lines.extend(item.as_debug_array(guess))

            print "%-16s %-10s %-10s %-10s %-10s" % ('category', 'actual', 'guessed', 'correct', 'incorrect')
            for key in sorted(actual_category_counts.iterkeys()):
                actual = self.dictionary_value(actual_category_counts, key)
                guessed = self.dictionary_value(guessed_category_counts, key)
                correct = self.dictionary_value(correct_category_counts, key)
                incorrect = self.dictionary_value(wrong_category_counts, key)
                print "%-16s %-10s %-10s %-10s %-10s" % (key, str(actual), str(guessed), str(correct), str(incorrect))

            classified_count = correct_count + wrong_count
            print("correct count:     %3d" % (correct_count))
            print("incorrect count:   %3d" % (wrong_count))
            print("classified count: %3d" % (classified_count))
            print("correct pct:       %f" % (float(correct_count) / float(classified_count) * 100.0))
            self.app.write_output_file('classify_summary.txt', summary_lines)
            self.app.write_output_file('classify_detail.txt', detail_lines)

        if True:
            print("nltk.classify.accuracy...")
            print nltk.classify.accuracy(classifier, train_set)
            print("nltk.classify.accuracy complete.")

        if True:
            print("classifier.show_most_informative_features...")
            classifier.show_most_informative_features(10)

        print('---')
        print('done')

    def dictionary_value(self, d, key):
        if d.has_key(key):
            return d[key]
        else:
            return 0

    def generate_training_category_file(self):
        feed_items = self.load_pickled_feed_items(self.app, {}, {})
        out_lines = []
        for fi in feed_items:
            line = "%s | UNCAT | %s - %s " % (fi.lookup_key(), fi.title, fi.feed_url)
            out_lines.append(line)
        out_lines.sort()
        self.app.write_data_file('training_categories_gen.txt', out_lines)

    def load_pickled_feed_items(self, app, categories, stop_words):
        feed_items = []
        dir_list = os.listdir(app.data_directory())
        for filename in dir_list:
            if filename.endswith(".pkl"):
                feed_number = self.parse_feed_number(filename)
                pkl_file = open(app.data_directory() + filename, 'r')
                feed = pickle.load(pkl_file)
                pkl_file.close()
                rf = locomotive.rss.RssFeed(feed, feed_number, stop_words)
                for fi in rf.items:
                    feed_items.append(fi)

        print '%d pickled feed items loaded' % (len(feed_items))
        return feed_items

    def parse_feed_number(self, filename):  # feed_9.pkl
        f = filename.replace('_', ' ')
        f = f.replace('.', ' ')
        s = f.split()[1]
        return int(s)

    def collect_all_words(self, items):
        words = []
        freqs = nltk.FreqDist()
        for item in items:
            item_words = item.all_words
            for w in item_words:
                words.append(w)
                # freqs.inc(w, 1)
                freqs[w] += 1

        print('collect_all_words count: ' + str(len(words)))  #
        self.app.write_output_file('words_all.txt', words)

        l = []
        for w in freqs.keys():
            l.append("%-30s  %d" % (w, freqs.get(w)))
        self.app.write_output_file('words_all_freq.txt', l)

        return words

    def identify_top_words(self, all_words):
        freq_dist = nltk.FreqDist(w.lower() for w in all_words)
        top_words = freq_dist.keys()[:1000]
        self.app.write_output_file('words_top.txt', top_words)
        return top_words

    # The following code relates to the nltk reuters data and its processing.

    def classify_reuters(self):
        metadata = self.read_reuters_metadata()
        stop_words = self.app.stop_words()
        all_words = []
        rss_items = self.read_training_articles(metadata, 999999, stop_words)
        self.app.write_output_file('rss_item_0.txt', rss_items[0].as_debug_array(''))
        for item in rss_items:
            for w in item.all_words:
                all_words.append(w)
        top_words = self.identify_top_words(all_words)

        featuresets = []
        for item in rss_items:
            features = item.features(top_words)
            tup = (features, item.category)  # tup is a 2-element tuple
            featuresets.append(tup)

        train_set = featuresets

        print('featuresets count: ' + str(len(featuresets)))

        print("training...")
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        print("training complete")

        if True:
            summary_lines = []
            actual_category_counts = {};
            guessed_category_counts = {}
            correct_category_counts = {};
            close_category_counts = {};
            wrong_category_counts = {}
            correct_count = 0;
            close_count = 0;
            wrong_count = 0;
            classified_count = 0
            for item in rss_items:
                feat = item.features(top_words)
                cat = item.category
                guess = classifier.classify(feat)
                item.guess = guess
                result = 'wrong'
                actual_category_counts[cat] = actual_category_counts.get(cat, 0) + 1
                guessed_category_counts[guess] = guessed_category_counts.get(guess, 0) + 1
                if item.category == guess:
                    result = 'correct'
                    item.result = result
                    correct_count = correct_count + 1
                    correct_category_counts[cat] = correct_category_counts.get(cat, 0) + 1
                else:
                    if item.in_category(guess):
                        result = 'close'
                        close_count = close_count + 1
                        item.result = result
                        close_category_counts[cat] = close_category_counts.get(cat, 0) + 1
                        self.app.write_output_file("item_%s_c.txt" % (item.item_number), item.as_debug_array(''))
                    else:
                        wrong_count = wrong_count + 1
                        wrong_category_counts[cat] = wrong_category_counts.get(cat, 0) + 1
                        self.app.write_output_file("item_%s_w.txt" % (item.item_number), item.as_debug_array(''))

                line = 'fn: %-6s  in: %-6s  actual: %-18s  guess: %-18s  %-s' % (
                    str(item.feed_number), str(item.item_number), cat, guess, result)
                summary_lines.append(self.app.to_unicode(line))

            print "%-16s %-10s %-10s %-10s %-10s" % ('category', 'actual', 'guessed', 'correct', 'incorrect')
            for key in sorted(actual_category_counts.iterkeys()):
                actual = self.dictionary_value(actual_category_counts, key)
                guessed = self.dictionary_value(guessed_category_counts, key)
                correct = self.dictionary_value(correct_category_counts, key)
                close = self.dictionary_value(close_category_counts, key)
                incorrect = self.dictionary_value(wrong_category_counts, key)
                print "%-16s %-10s %-10s %-10s %-10s %-10s" % (
                    key, str(actual), str(guessed), str(correct), str(close), str(incorrect))

            classified_count = correct_count + close_count + wrong_count
            correct_close_count = correct_count + close_count
            print("correct count:        %3d" % (correct_count))
            print("close count:          %3d" % (close_count))
            print("wrong count:          %3d" % (wrong_count))
            print("classified count:     %3d" % (classified_count))
            print("correct pct:          %f" % (float(correct_count) / float(classified_count) * 100.0))
            print("correct-or-close pct: %f" % (float(correct_close_count) / float(classified_count) * 100.0))
            self.app.write_output_file('classify_summary.txt', summary_lines)

        if False:
            print("nltk.classify.accuracy...")
            print nltk.classify.accuracy(classifier, train_set)
            print("nltk.classify.accuracy complete.")

        if False:
            print("classifier.show_most_informative_features...")
            classifier.show_most_informative_features(10)

        print('---')
        print('done')

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

    def knn_rss(self):
        categories = self.app.load_training_categories()
        stop_words = self.app.stop_words()
        feed_items = self.load_pickled_feed_items(self.app, categories, stop_words)
        all_words = self.collect_all_words(feed_items)
        top_words = self.identify_top_words(all_words)
        # random.shuffle(feed_items)

        data_arrays, data_labels = [], []

        for item in feed_items:
            item_data = item.knn_data(top_words)
            # print "item_data: %s \n%s " % (item.category, item_data)
            data_arrays.append(item_data)
            data_labels.append(item.category)

        data_group = array(data_arrays)
        correct_count = 0;
        wrong_count = 0

        for (i, item) in enumerate(feed_items):
            item_data = data_arrays[i]
            result = self.knn_classify(item_data, data_group, data_labels, 3)
            if result == item.category:
                correct_count = correct_count + 1
            else:
                wrong_count = wrong_count + 1
            # print str(item_data)
            pct_correct = (float(correct_count) / float(correct_count + wrong_count)) * 100.0
            print "item %d  cat: %s  guess: %s  correct: %d  wrong: %d  pct_correct: %f" % (
                i, item.category, result, correct_count, wrong_count, pct_correct)

        stop_words = self.app.stop_words()
        all_words = []
        metadata = ''
        self.rss_items = self.read_training_articles(metadata, 999999, stop_words)
        try:
            self.app.write_output_file('rss_item_0.txt', self.rss_items[0].as_debug_array(''))
        except Exception:
            print()


        for item in self.rss_items:
            for w in item.all_words:
                all_words.append(w)
        top_words = self.identify_top_words(all_words)
        category_array = self.collect_unique_categories_by_freq()

        data_arrays, data_labels = [], []

        for item in self.rss_items:
            data = item.knn_data(top_words)
            data_arrays.append(data)
            data_labels.append(item.category)

        data_group = array(data_arrays)
        correct_count = 0;
        wrong_count = 0

        for (i, item) in enumerate(self.rss_items):
            data = data_arrays[i]
            guess = self.knn_classify(data, data_group, data_labels, 3)
            if guess == item.category:
                correct_count = correct_count + 1
            else:
                wrong_count = wrong_count + 1
            pct_correct = (float(correct_count) / float(correct_count + wrong_count)) * 100.0
            print "item %d  %-22s  cat: %-16s  guess: %-16s  correct: %d  wrong: %d  pct_correct: %f" % (
                i, item.metadata, item.category, guess, correct_count, wrong_count, pct_correct)

    def collect_unique_categories_by_freq(self):
        freqs = nltk.FreqDist()
        sorted_cats = []
        for item in self.rss_items:
            for w in item.categories:
                # freqs.inc(w, 1)
                freqs[w] += 1
        for cat in freqs.keys():
            sorted_cats.append(cat)
            print "collect_sorted_categories: %s  %d" % (cat, freqs.get(cat))
        return sorted_cats

    def knn_simple(self):
        print "knn_simple categorization example:"
        dataset, labels = self.create_simple_dataset()
        print "dataset:\n%s" % (str(dataset))
        print "labels: %s" % (str(labels))
        test_cases = []
        test_cases.append([0.1, 0.1, 0.6])
        test_cases.append([0.5, 0.5, 0.6])
        test_cases.append([0.6, 0.6, 0.6])
        test_cases.append([0.9, 0.9, 0.6])
        for tc in test_cases:
            result = self.knn_classify(tc, dataset, labels, 3)
            print "result is %s for case %s , type: %s" % (result, str(tc), str(type(tc)))

    def create_simple_dataset(self):
        group = array([[1.0, 1.1, 0.5], [1.0, 1.0, 0.5], [0.0, 0.0, 0.5], [0.0, 0.1, 0.5]])
        labels = ['A', 'A', 'B', 'B']
        return group, labels

    def knn_classify(self, inX, dataSet, labels, k):
        dataSetSize = dataSet.shape[0]
        diffMat = tile(inX, (dataSetSize, 1)) - dataSet
        sqDiffMat = diffMat ** 2
        sqDistances = sqDiffMat.sum(axis=1)
        distances = sqDistances ** 0.5
        classCount = {}
        sortedDistIndicies = distances.argsort()
        for i in range(k):
            voteIlabel = labels[sortedDistIndicies[i]]
            if classCount.has_key(voteIlabel):
                classCount[voteIlabel] += 1
            else:
                classCount[voteIlabel] = 1
        sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sortedClassCount[0][0]
