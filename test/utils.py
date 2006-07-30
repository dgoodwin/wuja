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

    def __init__(self, urls, feed_source=None):
        super(WujaConfiguration, self).__init__()
        self.observers = []
        self.urls = urls
        if feed_source is None:
            self.feed_source = TestFeedSource()
        else:
            self.feed_source = feed_source

    def get_feed_urls(self):
        return self.urls

    def add_feed_url(self, url):
        self.urls.append(url)
        self.emit("config-changed")

    def remove_feed_url(self, url):
        self.urls.remove(url)
        self.emit("config-changed")

    def remove_all_feed_urls(self):
        self.urls = []
        self.emit("config-changed")

    def get_feed_source(self):
        return self.feed_source

class TestFeedSource(FeedSource):
    """ We need to do some fairly tricky things with feeds to test
    certain components. (i.e. return a calendar, add/remove entries
    from the feed, return new calendar with new last update time)

    A TestFeedSource can be configured to return certain calendar
    objects and does not communicate with the network.
    """

    def __init__(self):
        self.last_update = "a"

        # Map fake calendar URL to CalendarData:
        self.calendars = {}

    def get_calendar(self, url):
        if not self.calendars.has_key(url):
            raise Exception("TestFeedSource not configured for url: %s" %
                url)
        cal_data = self.calendars[url]
        cal = cal_data.build()
        all_entries = []
        all_entries.extend(cal_data.single_entries)
        all_entries.extend(cal_data.recurring_entries)
        for entry in all_entries:
            entry.build(cal)
        return cal

    def get_feed_last_update(self, url):
        """ Override for fake data and no network communication. """
        return self.calendars[url].last_update

class CalendarData:
    """ Dummy Calendar object, used for configuring the TestFeedSource
    without actually creating a database object.
    """
    def __init__(self, title, last_update, url):
        self.title = title
        self.last_update = last_update
        self.url = url
        self.single_entries = [] # single occurrence entry data
        self.recurring_entries = [] # recurring entry data

    def build(self):
        return Calendar(title=self.title, last_update=self.last_update,
            url=self.url)

class SingleOccurrenceEntryData:
    """ Dummy SingleOccurrenceEntry object, used for configuring the
    TestFeedSource without actually creating a database object.
    """
    def __init__(self, title, time, reminder, location):
        self.title = title
        self.time = time
        self.reminder = reminder
        self.location = location

        self.entry_id = "FakeEntryId"
        self.description = ""
        self.updated = "whenever"
        self.duration = 3600

    def build(self, cal):
        return SingleOccurrenceEntry(entry_id=self.entry_id, title=self.title,
            description=self.description, reminder=self.reminder,
            updated=self.updated, time=self.time, duration=self.duration,
            location=self.location, calendar=cal)

class RecurringEntryData:
    """ Dummy RecurringEntry object, used for configuring the
    TestFeedSource without actually creating a database object.
    """
    def __init__(self, title, reminder, location, recurrence):
        self.title = title
        self.reminder = reminder
        self.location = location
        self.recurrence = recurrence

        self.entry_id = "FakeEntryId"
        self.description = ""
        self.updated = "whenever"

    def build(self, cal):
        return RecurringEntry(entry_id=self.entry_id, title=self.title,
            description=self.description, reminder=self.reminder,
            location=self.location, updated=self.updated,
            recurrence=self.recurrence, calendar=cal)

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
