""" Objects and methods used for testing. """

__revision__ = "$Revision$"

from wuja.config import WujaConfiguration
from wuja.feed import FeedSource

from samplefeed import xml

class TestWujaConfiguration(WujaConfiguration):
    """ A fake configuration object that doesn't actually talk to
    gconf.
    """

    def __init__(self, urls):
        self.observers = []
        self.urls = urls

    def get_feed_urls(self):
        return self.urls

    def add_feed_url(self, url):
        self.urls.append(url)
        self.notify_configuration_changed()

    def remove_feed_url(self, url):
        self.urls.remove(url)
        self.notify_configuration_changed()

    def remove_all_feed_urls(self):
        self.urls = []
        self.notify_configuration_changed()

    def get_feed_source(self):
        return TestFeedSource()

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

