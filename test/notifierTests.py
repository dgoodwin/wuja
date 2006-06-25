import unittest
from datetime import datetime, timedelta

import settestpath

from wuja.notifier import Notifier, DEFAULT_THRESHOLD
from wuja.model import SingleOccurrenceEntry
from wuja.config import WujaConfiguration

TEST_GCONF_PATH = '/apps/wuja/test'

class TestNotifier(Notifier):
    """
    Notifier class talks directly with Google's servers to fetch actual
    feeds. For testing we'll use a subclass so we can pass in the entries we
    want.
    """
    def __init__(self, entries):

        # Test notifier won't actually call any methods on the configuration:
        config = WujaConfiguration(TEST_GCONF_PATH)

        Notifier.__init__(self, config)
        self.calendar_entries = entries
        self.update()
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

    def notify(self, event):
        self.notified = True
        self.trigger_entry = event.entry
        self.trigger_event = event

class NotifierTests(unittest.TestCase):

    def testSimpleNotification(self):
        future_time = datetime.now() + timedelta(minutes=10)
        self.__create_entry(future_time)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)
        self.assertEqual(self.entry, self.observer.trigger_entry)

    def test_notification_beyond_threshold(self):
        future_time = datetime.now() + timedelta(minutes=DEFAULT_THRESHOLD,
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

    def __create_entry(self, future_time):
        self.entry = SingleOccurrenceEntry("fakeId", "Fake Title", "",
            datetime.now(), future_time, 3600, "Gumdrop Alley")
        self.notifier = TestNotifier([self.entry])
        self.observer = TestObserver()
        self.notifier.attach(self.observer)
        self.assertFalse(self.observer.notified)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NotifierTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

