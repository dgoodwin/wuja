""" Tests for feeds. """

__revision__ = "$Revision$"

import unittest
import settestpath

from datetime import datetime

from wuja.feed import FeedSource, parse_timestamp, build_calendar
from samplefeed import xml

from utils import TestFeedSource, setupDatabase

setupDatabase()

FEED_URL = "http://whatever.com/feedurl"
FEED_TITLE = "Wuja Testing Calendar"
FEED_LAST_UPDATE = "Doesn't matter."

class FeedSourceTests(unittest.TestCase):

    def test_simple_entry(self):
        cal = build_calendar(xml, FEED_LAST_UPDATE, FEED_URL)
        distant_event = find_entry(cal.entries, "Distant Event")
        self.assertTrue(distant_event != None)

    def test_timestamp_parsing(self):
        timestamp = "2006-05-18T15:24:41.000Z"
        date = parse_timestamp(timestamp)
        self.assertEquals(2006, date.year)
        self.assertEquals(15, date.hour)
        self.assertEquals(24, date.minute)
        self.assertEquals(41, date.second)

def find_entry(entries, title):
    for entry in entries:
        if entry.title == title:
            return entry
    raise Exception('Unable to find calendar event: "' + title + '"')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeedSourceTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

