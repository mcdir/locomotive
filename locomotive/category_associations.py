
import codecs
import locale
import nltk
import numpy
import sys

import locomotive

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

class CategoryAssociations:

    def __init__(self, category_array):
        self.category_array = category_array
        self.category_hash  = self.initialize_category_idx_hash()
        self.matrix = self.initialize_matrix() # matrix is a numpy 2-dimension array

    def initialize_category_idx_hash(self):
        hash = {}
        for (i, cat) in enumerate(self.category_array):
            hash[cat] = i
            hash[i] = cat
        return hash

    def initialize_matrix(self):
        return numpy.zeros((self.size(), self.size())) # default to numpy.float64 elements

    def size(self):
        return len(self.category_array)

    def lookup(self, cat):
        if self.category_hash.has_key(cat):
            return self.category_hash[cat]
        else:
            return -1

    def increment(self, cat1, cat2, incr):
        idx1 = self.lookup(cat1)
        idx2 = self.lookup(cat2)
        if self.valid_coordinates(idx1, idx2):
            curr = self.value(idx1, idx2)
            new_val = curr + float(incr)
            self.matrix[idx1][idx2] = new_val
            return new_val
        else:
            return -1

    def value(self, idx1, idx2):
        if self.valid_coordinates(idx1, idx2):
            return self.matrix[idx1][idx2]
        else:
            return -1

    def valid_coordinates(self, idx1, idx2):
        i1 = int(idx1); i2 = int(idx2)
        if (i1 >= 0) and (i2 >= 0) and (i1 < self.size()) and (i2 < self.size()):
            return True
        else:
            return False

    def associations(self, cat):
        # see API at http://nltk.googlecode.com/svn/trunk/doc/api/nltk.probability.FreqDist-class.html
        freqs   = nltk.FreqDist()
        cat_idx = self.lookup(cat)
        for i in range(self.size()):
            val = self.value(cat_idx, i)
            if val > 0:
                assoc_cat = self.lookup(i)
                freqs[assoc_cat] += val
        return(freqs)

    def display(self):
        print "CategoryAssociations:\nsize: %d\n%s\n%s\n%s\n" % (self.size(), self.category_array, self.category_hash, self.matrix)

