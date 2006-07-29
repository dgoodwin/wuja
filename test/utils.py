""" Objects and methods used for testing. """

__revision__ = "$Revision$"

import sqlobject

from wuja.config import WujaConfiguration
from wuja.feed import FeedSource
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Calendar

from samplefeed import xml

class TestWujaConfiguration(WujaConfiguration):
    """ A fake configuration object that doesn't actually talk to
    gconf.
    """

    def __init__(self, urls):
        super(WujaConfiguration, self).__init__()
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
    """ Override FeedSource for testing so we never actually hit the
    network.
    """

    def __init__(self):
        self.last_update = "a"
        self.override_calendars = {}

    def get_calendar(self, url):
        if self.override_calendars.has_key(url):
            return self.override_calendars[url]
        else:
            return FeedSource.get_calendar(self, url)

    def _get_feed_last_update(self, url):
        """ Override for fake data and no network communication. """
        return self.last_update

    def _get_feed_xml(self, url):
        return xml

def setupDatabase():
    """ Configure SQLObject to use an in-memory SQLite database and
    create the proper tables. Should be called in the setUp() of any
    test suite using persistent objects.
    """
    connection = sqlobject.connectionForURI('sqlite:/:memory:')
    sqlobject.sqlhub.processConnection = connection

    Calendar.createTable(ifNotExists=True)
    SingleOccurrenceEntry.createTable(ifNotExists=True)
    RecurringEntry.createTable(ifNotExists=True)

def teardownDatabase():
    """ Wipe out database tables. Should be called in the
    tearDown of any test suite using persistent objects.
    """
    Calendar.clearTable()
    SingleOccurrenceEntry.clearTable()
    RecurringEntry.clearTable()
