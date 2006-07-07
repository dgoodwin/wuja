""" Objects and methods used for testing. """

__revision__ = "$Revision$"

from wuja.config import WujaConfiguration
from wuja.feed import FeedSource

from samplefeed import xml

class TestWujaConfiguration:

    def get_feed_source(self):
        return TestFeedSource(self)

class TestFeedSource(FeedSource):
    """ Builds feed objects without ever actually hitting the network. """

    def __init__(self):
        FeedSource.__init__(self)
        self.last_update = "a"

    def _get_feed_last_update(self, url):
        """ Override for fake data and no network communication. """
        return self.last_update

    def _get_feed_xml(self, url):
        return xml

