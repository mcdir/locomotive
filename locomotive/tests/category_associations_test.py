import os
import logging
import unittest
import sys 
import locomotive

class CategoryAssociationTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(stream=sys.stdout)
        logging.getLogger("CategoryAssociationTest").setLevel(logging.DEBUG)
        self.app  = locomotive.app.Application() 
        self.cats = ['tebow', 'jets', 'nfl', 'ny', 'boeing_747']
        self.ca   = locomotive.category_associations.CategoryAssociations(self.cats)

    def tearDown(self):
        pass

    def test_size(self):
        self.assertEqual(5, self.ca.size()) 
 
    def test_matrix_shape(self):
        shape = str(self.ca.matrix.shape)
        self.assertEqual('(5, 5)', shape) 

    def test_valid_coordinates(self):
        self.assertFalse(self.ca.valid_coordinates(3,5)) 
        self.assertFalse(self.ca.valid_coordinates(5,3))
        self.assertFalse(self.ca.valid_coordinates(-1,3))
        self.assertFalse(self.ca.valid_coordinates(1,-3)) 
        self.assertTrue(self.ca.valid_coordinates(0,0))
        self.assertTrue(self.ca.valid_coordinates(4,4))
        self.assertTrue(self.ca.valid_coordinates(4.9,0.9)) 
        self.assertFalse(self.ca.valid_coordinates(5.1,3))
        self.assertFalse(self.ca.valid_coordinates(3,5.1))
        self.assertFalse(self.ca.valid_coordinates(-5.1,3))
        self.assertFalse(self.ca.valid_coordinates(3,-5.1))

    def test_lookup(self):
        self.assertEqual(-1, self.ca.lookup('locomotive'))
        self.assertEqual(0, self.ca.lookup('tebow'))
        self.assertEqual(4, self.ca.lookup('boeing_747'))
        self.assertEqual('boeing_747', self.ca.lookup(4)) 

    def test_incrementing(self):
        self.assertEqual(-1, self.ca.increment('not','there',1))
        self.assertEqual(-1, self.ca.increment('not','ny',1))
        self.assertEqual(2, self.ca.increment('jets','ny',2))
        self.assertEqual(3, self.ca.increment('jets','ny',1))
        self.assertEqual(3, self.ca.increment('jets','ny',0)) 
        self.assertEqual(1, self.ca.increment('jets','boeing_747',1))  
        self.assertEqual(1, self.ca.increment('boeing_747','jets',1)) 
        self.assertEqual(2, self.ca.increment('jets','ny',-1))

        i1 = self.ca.lookup('jets')
        i2 = self.ca.lookup('ny')
        self.assertEqual(2, self.ca.value(i1,i2))

        #self.ca.display()

        assoc = self.ca.associations('not')
        self.assertEqual(0, len(assoc))

        assoc = self.ca.associations('jets')
        self.assertEqual(2, len(assoc))
        self.assertEqual('ny', assoc.keys()[0])
        self.assertEqual('boeing_747', assoc.keys()[1])

        assoc = self.ca.associations('boeing_747')

        for (i, cat) in enumerate(self.cats):
            assoc = self.ca.associations(cat)
            #print "assoc for cat: %-10s %s" % (cat, assoc)  

    def test_similar_categories(self):
        self.assertEqual(-1, self.ca.lookup('locomotive'))
        self.assertEqual(0, self.ca.lookup('tebow'))
        self.assertEqual(4, self.ca.lookup('boeing_747')) 

    def log(self, msg):
        log = logging.getLogger("CategoryAssociationTest")
        log.debug(str(msg))
 