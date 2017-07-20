
import codecs
import locale
import nltk
from nltk.corpus import names
import random
import sys

'''
This is a modified version of a good example program in the O'Reilly NLTK book.
'''

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

def gender_features(word):
    return {'last_letter': word[-1], 'last_letter': word[-2]}

def process_names():
    all_names = []

    # nltk names data is in /Users/cjoakim/nltk_data/corpora/names
    # xxx_names are arrays of 2-element tuples like: ('Susana', 'female')
    m_names = [(name, 'male') for name in names.words('male.txt')]
    f_names = [(name, 'female') for name in names.words('female.txt')]
    all_names.extend(m_names)
    all_names.extend(f_names)
    print('m names count:   ' + str(len(m_names)))
    print('f names count:   ' + str(len(f_names)))
    print('all names count: ' + str(len(all_names)))
    random.shuffle(all_names)

    if False:
        print(all_names)
        for (n,g) in all_names:
            print('gender: ' + g + '  name: ' + n)

    featuresets = [(gender_features(n), g) for (n,g) in all_names]
    print('featuresets type: ' + str(type(featuresets))) # <type 'list'>

    test_names    = all_names[:500]
    devtest_names = all_names[500:1500]
    train_names   = all_names[1500:]

    train_set     = [(gender_features(n), g) for (n,g) in train_names]
    devtest_set   = [(gender_features(n), g) for (n,g) in devtest_names]
    test_set      = [(gender_features(n), g) for (n,g) in test_names]

    print('train_set count:   ' + str(len(train_set)))   # 6444
    print('devtest_set count: ' + str(len(devtest_set))) # 1000
    print('test_set count:    ' + str(len(test_set)))    #  500

    # Having divided the corpus into appropriate datasets, we train a model using the training set.
    # and then run it on the dev-test set.
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    test_names = ['Christopher', 'Theresa', 'martin', 'jelka', 'neo', 'trinity']
    for name in test_names:
        sex = classifier.classify(gender_features(name))
        print('' + name + ' sex is: ' + sex)

    print nltk.classify.accuracy(classifier, devtest_set) #

    classifier.show_most_informative_features(10)
    '''
        Most Informative Features                            (likelihood ratios)
             last_letter = 'a'            female : male   =     35.9 : 1.0
             last_letter = 'k'              male : female =     31.7 : 1.0
             last_letter = 'f'              male : female =     17.3 : 1.0
             last_letter = 'p'              male : female =     12.5 : 1.0
             last_letter = 'd'              male : female =      9.9 : 1.0
             last_letter = 'm'              male : female =      9.8 : 1.0
             last_letter = 'o'              male : female =      8.1 : 1.0
        next_last_letter = 'o'              male : female =      7.8 : 1.0
             last_letter = 'v'              male : female =      7.8 : 1.0
        next_last_letter = 'u'              male : female =      7.2 : 1.0
    '''

    for (name, tag) in devtest_names:
        guess = classifier.classify(gender_features(name))
        if guess != tag:
            print 'incorrect; actual: %-8s  guess:%-8s  name: %-30s' % (tag, guess, name)

process_names()

print('done')
