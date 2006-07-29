""" Tests for the notifier module. """

__revision__ = "$Revision$"

import unittest
from datetime import datetime, timedelta

import settestpath

from wuja.notifier import Notifier
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Calendar
from wuja.config import WujaConfiguration

from utils import TestWujaConfiguration, setupDatabase, teardownDatabase
from sampledata import weekly_recurrence_all_day

TEST_GCONF_PATH = '/apps/wuja/test'
REMIND = 10
CAL_TITLE = "Testing Calendar"
CAL_URL = "http://fakeurl"
CAL_LAST_UPDATE = "whenever"

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

    def setUp(self):
        setupDatabase()
        self.cal = Calendar(title=CAL_TITLE, last_update="somedate",
            url=CAL_URL)

    def tearDown(self):
        teardownDatabase()

    def testSimpleNotification(self):
        future_time = datetime.now() + timedelta(minutes=10)
        self.__create_entry(future_time)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)
        self.assertEqual(self.entry, self.observer.trigger_entry)

    def test_notification_beyond_threshold(self):
        future_time = datetime.now() + timedelta(minutes=REMIND,
            seconds=1)
        self.__create_entry(future_time)
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)
        self.assertEqual(None, self.observer.trigger_entry)

    def test_past_event(self):
        past_time = datetime.now() - timedelta(minutes=30)
        self.__create_entry(past_time)
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)
        self.assertEqual(None, self.observer.trigger_entry)

    def test_event_confirmed(self):
        event_time = datetime.now() + timedelta(minutes=2)
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
        event_time = datetime.now() + timedelta(minutes=2)
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

    def test_calendar_updated_entries_removed(self):
        # Create a calendar with two entries:
        cal = Calendar(title=CAL_TITLE, last_update=CAL_LAST_UPDATE,
            url=CAL_URL)
        single_entry = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=datetime.now(), duration=3600, location=LOCATION, calendar=cal)
        recur_entry = RecurringEntry(entry_id="fakeId",
            title=RECURRING_TITLE, description="",
            reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=weekly_recurrence_all_day, calendar=cal)

    def __create_entry(self, future_time):
        self.entry = SingleOccurrenceEntry(entry_id="fakeId",
            title="Fake Title", description="",reminder=REMIND,
            updated=datetime.now(), time=future_time, duration=3600,
            location="Gumdrop Alley", calendar=self.cal)
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

