""" Tests for the feedparser module. """

__revision__ = "$Revision$"

import unittest
import settestpath

from datetime import datetime

from wuja.feedparser import FeedParser, parse_timestamp
from samplefeed import xml

class ParsingTests(unittest.TestCase):

    # One entry, no recurrence:
    def test_simple_entry(self):
        feed_parser = FeedParser(xml)
        entries = feed_parser.entries

        distant_event = find_entry(entries, "Distant Event")
        self.assertTrue(distant_event != None)

    def test_timestamp_parsing(self):
        timestamp = "2006-05-18T15:24:41.000Z"
        date = parse_timestamp(timestamp)
        self.assertEquals(2006, date.year)
        self.assertEquals(15, date.hour)
        self.assertEquals(24, date.minute)
        self.assertEquals(41, date.second)

    def test_get_feed_title(self):
        feed_parser = FeedParser(xml)
        self.assertEqual("Wuja Testing Calendar", feed_parser.title)

def find_entry(entries, title):
    for entry in entries:
        if entry.title == title:
            return entry
    raise Exception('Unable to find calendar event: "' + title + '"')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ParsingTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

