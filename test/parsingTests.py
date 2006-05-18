import unittest
import settestpath

import urllib2
from elementtree.ElementTree import parse

class ParsingTests(unittest.TestCase):

    def testSimpleParsing(self):
        tree = parse('samplefeed.xml')
        root = tree.getroot()
        print root

def suite():
    return unittest.makeSuite(ParsingTests)

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

