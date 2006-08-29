#   Wuja - Google Calendar (tm) notifications for the GNOME desktop.
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" Objects and methods used for testing. """

__revision__ = "$Revision$"

import os
import os.path

from wuja.config import WujaConfiguration
from wuja.feed import FeedSource
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Calendar, Cache
from wuja.data import WUJA_DIR

from samplefeed import xml

TEST_DB_FILE = "test.db"

class TestWujaConfiguration(WujaConfiguration):

    """
    A fake configuration object that doesn't actually talk to
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
        self.db_file = TEST_DB_FILE

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

    def get_cache(self):
        return TestCache(self)


class TestCache(Cache):

    """ In-memory cache. """

    def __init__(self, db):
        """
        Override the Cache contructor to just create an in-memory
        dictionary instead of hitting the filesystem.
        """
        self._cache = {}


class TestFeedSource(FeedSource):

    """
    We need to do some fairly tricky things with feeds to test
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

    """
    Dummy Calendar object, used for configuring the TestFeedSource
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

    """
    Dummy SingleOccurrenceEntry object, used for configuring the
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
        return SingleOccurrenceEntry(self.entry_id, self.title,
            self.description, self.reminder, self.updated, self.time,
            self.duration, self.location)

class RecurringEntryData:

    """
    Dummy RecurringEntry object, used for configuring the
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
        return RecurringEntry(self.entry_id, self.title,
            self.description, self.reminder,
            self.location, self.updated,
            self.recurrence)


def teardownDatabase():
    """
    Wipe out database tables. Should be called in the
    tearDown of any test suite using persistent objects.
    """
    db_file = os.path.join(WUJA_DIR, TEST_DB_FILE)
    if os.path.exists(db_file):
        os.remove(db_file)

