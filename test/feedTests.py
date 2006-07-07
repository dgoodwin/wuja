""" Tests for feeds. """

__revision__ = "$Revision$"

import unittest
import settestpath

from datetime import datetime

from wuja.feed import Feed, FeedSource, parse_timestamp
from samplefeed import xml

from utils import TestFeedSource

FEED_URL = "http://whatever.com/feedurl"
FEED_TITLE = "Wuja Testing Calendar"
FEED_LAST_UPDATE = "Doesn't matter."

class FeedTests(unittest.TestCase):

    def test_simple_entry(self):
        feed = Feed(xml, FEED_LAST_UPDATE)
        entries = feed.entries

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
        feed = Feed(xml, FEED_LAST_UPDATE)
        self.assertEqual(FEED_TITLE, feed.title)

class FeedSourceTests(unittest.TestCase):
    """ Test the feed source functionality that isn't specific to
    actually communicating with Google servers.
    """

    def test_cached_feed(self):
        """ Request a feed, request again, ensure same feed object is
        returned.
        """
        feed_source = TestFeedSource()
        feed_source.last_updated = "a"
        feed = feed_source.get_feed(FEED_URL)
        self.assertEqual(FEED_TITLE, feed.title)
        self.assertEqual("a", feed.last_update)

        feed2 = feed_source.get_feed(FEED_URL)
        self.assertEqual("a", feed2.last_update)

    def test_rerequest_feed(self):
        """ Request a feed, change the last update time, rerequest and
        ensure we got a new feed object.
        """
        feed_source = TestFeedSource()
        feed_source.last_updated = "a"
        feed = feed_source.get_feed(FEED_URL)
        self.assertEqual("a", feed.last_update)

        # Change the last updated time:
        feed_source.last_update = "b"
        feed2 = feed_source.get_feed(FEED_URL)
        self.assertEqual("b", feed2.last_update)

def find_entry(entries, title):
    for entry in entries:
        if entry.title == title:
            return entry
    raise Exception('Unable to find calendar event: "' + title + '"')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeedTests))
    suite.addTest(unittest.makeSuite(FeedSourceTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

