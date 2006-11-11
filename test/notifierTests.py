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

""" Tests for the notifier module. """

__revision__ = "$Revision$"

import unittest
from datetime import datetime, timedelta

import settestpath

from wuja.notifier import Notifier
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Calendar
from wuja.config import WujaConfiguration

import utils
from utils import TestWujaConfiguration, teardownDatabase, TestCache
from sampledata import weekly_recurrence_all_day
from dateutil.tz import tzlocal

TEST_GCONF_PATH = '/apps/wuja/test'
REMIND = 10
CAL_TITLE = "Testing Calendar"
CAL_URL = "http://fakeurl"
CAL_LAST_UPDATE = "whenever"
CAL_TZ = "America/Halifax"
TZ = tzlocal()

TITLE = "Single Occurrence Entry Title"
RECURRING_TITLE = "Moo"
DESCRIPTION = "Some event."
REMIND = 20
UPDATED = "whenever"
LOCATION = "somewhere"

class TestNotifier(Notifier):
    """
    Notifier class talks directly with Google's servers to fetch actual
    feeds. For testing we'll use a subclass so we can pass in the entries we
    want.
    """
    def __init__(self, entries):

        urls = []
        urls.append("http://fake.url.google.com/blahblahblah")
        config = TestWujaConfiguration(urls)

        Notifier.__init__(self, config)
        self.calendar_entries = entries
        self.update_events()

    def update(self):
        """
        Override the parent method that actually updates feeds from Google.
        We were provided a list of entries and there's no need to update them.
        """
        pass

class TestObserver:
    def __init__(self):
        self.notified = False
        self.trigger_entry = None
        self.trigger_event = None

    def notify(self, notifier, event):
        self.notified = True
        self.trigger_entry = event.entry
        self.trigger_event = event

class NotifierTests(unittest.TestCase):

    def tearDown(self):
        teardownDatabase()

    def test_simple_notification(self):
        future_time = datetime.now(TZ) + timedelta(minutes=10)
        self.__create_entry(future_time)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)
        self.assertEqual(self.entry, self.observer.trigger_entry)

    def test_notification_beyond_threshold(self):
        future_time = datetime.now(TZ) + timedelta(minutes=REMIND,
            seconds=1)
        self.__create_entry(future_time)
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)
        self.assertEqual(None, self.observer.trigger_entry)

    def test_past_event(self):
        past_time = datetime.now(TZ) - timedelta(minutes=30)
        self.__create_entry(past_time)
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)
        self.assertEqual(None, self.observer.trigger_entry)

    def test_event_confirmed(self):
        event_time = datetime.now(TZ) + timedelta(minutes=2)
        self.__create_entry(event_time)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)
        self.assertEqual(self.entry, self.observer.trigger_entry)

        # Accept the event:
        self.observer.trigger_event.accepted = True

        # Reset the observer and make sure he's not renotified:
        self.observer.notified = False
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)

    def test_confirm_event_and_update_feeds(self):
        event_time = datetime.now(TZ) + timedelta(minutes=2)
        self.__create_entry(event_time)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)

        # Accept the event:
        self.observer.trigger_event.accepted = True

        # Reset the observer and make sure he's not renotified:
        self.observer.notified = False
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)

        # Update events (normally called after feeds are updated) and
        # ensure the accepted status of our event remains:
        self.notifier.update_events()
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)

    def test_initial_update(self):
        test_feed_source = utils.TestFeedSource()
        cal = self.__create_test_calendar_data()
        test_feed_source.calendars[CAL_URL] = cal
        urls = [CAL_URL]
        test_config = TestWujaConfiguration(urls, feed_source=test_feed_source)

        cache = TestCache(test_config.db_file)
        self.assertEqual(0, len(cache.load_all()))
        self.notifier = Notifier(test_config, cache)

        # Check that our objects were created:
        self.assertEqual(1, len(cache.load_all()))

    def test_feed_deleted_from_config(self):
        test_feed_source = utils.TestFeedSource()
        cal = self.__create_test_calendar_data()
        test_feed_source.calendars[CAL_URL] = cal
        urls = [CAL_URL]
        test_config = TestWujaConfiguration(urls, feed_source=test_feed_source)

        cache = TestCache(test_config.db_file)
        self.assertEqual(0, len(cache.load_all()))
        self.notifier = Notifier(test_config, cache)

        # Check that our objects were created:
        self.assertEqual(1, len(cache.load_all()))

        test_config.remove_feed_url(CAL_URL)
        self.assertEqual(0, len(cache.load_all()))

    def test_feed_updated_entries_added(self):
        test_feed_source = utils.TestFeedSource()
        cal = self.__create_test_calendar_data()
        test_feed_source.calendars[CAL_URL] = cal
        urls = [CAL_URL]
        test_config = TestWujaConfiguration(urls, feed_source=test_feed_source)

        cache = TestCache(test_config.db_file)
        self.assertEqual(0, len(cache.load_all()))
        self.notifier = Notifier(test_config, cache)

        # Check that our objects were created:
        self.assertEqual(1, len(cache.load_all()))

        # Add a new entry:
        cal.entries.append(SingleOccurrenceEntry("singleid",
            "Another Entry", "desc", REMIND, datetime.now(TZ), datetime.now(TZ),
            3600, "Another location.", cal))
        cal.last_update = "new time" # change last update time
        self.notifier.update()
        self.assertEqual(1, len(cache.load_all()))

    def test_feed_updated_entries_removed(self):
        test_feed_source = utils.TestFeedSource()
        cal = self.__create_test_calendar_data()
        test_feed_source.calendars[CAL_URL] = cal
        urls = [CAL_URL]
        test_config = TestWujaConfiguration(urls, feed_source=test_feed_source)

        cache = TestCache(test_config.db_file)
        self.assertEqual(0, len(cache.load_all()))
        self.notifier = Notifier(test_config, cache)

        # Check that our objects were created:
        self.assertEqual(1, len(cache.load_all()))

        # Remove an entry:
        cal.entries.pop()
        cal.last_update = "new time" # change last update time
        self.notifier.update()
        self.assertEqual(1, len(cache.load_all()))

    def __create_test_calendar_data(self):
        # Create a calendar with two entries:
        cal = Calendar(CAL_TITLE, CAL_URL, "0", CAL_TZ)
        cal.entries.append(SingleOccurrenceEntry("singleid",
            TITLE, "desc", REMIND, datetime.now(TZ), datetime.now(TZ), 3600,
            LOCATION, cal))
        cal.entries.append(RecurringEntry("id2", TITLE + " Recur",
            "", REMIND, LOCATION, datetime.now(TZ), weekly_recurrence_all_day,
            cal))
        return cal

    def __create_entry(self, future_time):
        cal = Calendar(CAL_TITLE, "somedate", CAL_URL, CAL_TZ)
        self.entry = SingleOccurrenceEntry("fakeId", "Fake Title", "",REMIND,
            datetime.now(TZ), future_time, 3600, "Gumdrop Alley", cal)
        self.notifier = TestNotifier([self.entry])
        self.observer = TestObserver()
        self.notifier.connect("feeds-updated", self.observer.notify)
        self.assertFalse(self.observer.notified)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NotifierTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

