
import codecs
import locale
import nltk
from nltk.corpus import movie_reviews
import random
import sys

'''
This is a modified version of a good example program in the O'Reilly NLTK book.
'''

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

def load_movie_reviews():
    reviews = [(list(movie_reviews.words(fileid)), category) for category in movie_reviews.categories() for fileid in movie_reviews.fileids(category)]
    random.shuffle(reviews)
    print('' + str(len(reviews)) + ' reviews loaded') # 2000
    if False:
        doc = reviews[0]
        print('doc type: ' + str(type(doc)) + ' length: ' + str(len(doc)))
        for elem in doc:
          print('elem type: ' + str(type(elem)) + ' length: ' + str(len(elem)))
        '''
        doc type: <type 'tuple'> length: 2
          elem type: <type 'list'> length: 711  <- array of words in the movie review
          elem type: <type 'str'>  length: 3    <- 'pos', meaning positive review
        '''
    return reviews

def collect_all_words(reviews):
    words = []
    for review in reviews:
        review_words = review[0]
        for word in review_words:
            words.append(word)
    print('collect_all_words count: ' + str(len(words))) # 1583820
    if False:
        sample_words = words[:500]
        for word in sample_words:
            print('sample_word: ' + word)
    return words

def identify_top_words(all_words):
    freq_dist = nltk.FreqDist(w.lower() for w in all_words)
    print('freq_dist: ' + str(type(freq_dist)) + ' length: ' + str(len(freq_dist)))
    # freq_dist: <class 'nltk.probability.FreqDist'> length: 39768
    top_words = freq_dist.keys()[:2000]
    print('top_words: ' + str(type(top_words)) + ' length: ' + str(len(top_words)))
    if False:
        for word in top_words:
            print('top_word: ' + word)
    return top_words

def document_features(document_words, word_features):
    doc_word_set = set(document_words)
    doc_features = {}
    for word in word_features:
        doc_features['contains(%s)' % word] = (word in doc_word_set)
    return doc_features

def process_movies():
    documents = load_movie_reviews()
    all_words = collect_all_words(documents)
    word_features = identify_top_words(all_words)
    print('word_features: ' + str(type(word_features)) + ' length: ' + str(len(word_features)))

    df = document_features(documents[0][0], word_features)

    featuresets = [(document_features(d, word_features), category) for (d,category) in documents]
    test_set    = featuresets[:100]
    devtest_set = featuresets[100:200]
    train_set   = featuresets[200:]

    print('featuresets count: ' + str(len(featuresets)))  # 2000
    print('test_set count:    ' + str(len(test_set)))     #  100
    print('devtest_set count: ' + str(len(devtest_set)))  #  100
    print('train_set count:   ' + str(len(train_set)))    # 1800

    classifier = nltk.NaiveBayesClassifier.train(train_set)
    print nltk.classify.accuracy(classifier, test_set) # 0.8
    classifier.show_most_informative_features(10)
    '''
        Most Informative Features
           contains(outstanding) = True              pos : neg    =     10.3 : 1.0
                 contains(mulan) = True              pos : neg    =      8.2 : 1.0
                contains(seagal) = True              neg : pos    =      7.9 : 1.0
                 contains(damon) = True              pos : neg    =      7.5 : 1.0
           contains(wonderfully) = True              pos : neg    =      6.3 : 1.0
                contains(poorly) = True              neg : pos    =      5.8 : 1.0
                 contains(awful) = True              neg : pos    =      5.2 : 1.0
            contains(ridiculous) = True              neg : pos    =      5.2 : 1.0
                  contains(lame) = True              neg : pos    =      5.1 : 1.0
                contains(wasted) = True              neg : pos    =      5.0 : 1.0
    '''

    for doc in documents:
        df = document_features(doc[0], word_features)
        cat = doc[1]
        guess = classifier.classify(df)
        if guess != cat:
            print 'incorrect; actual: %-8s  guess:%-8s' % (cat, guess)

process_movies()

print('done')
