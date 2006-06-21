import unittest
from datetime import datetime, timedelta

import settestpath

from wuja.notifier import Notifier, DEFAULT_THRESHOLD
from wuja.model import SingleOccurrenceEntry

class TestNotifier(Notifier):
    """
    Notifier class talks directly with Google's servers to fetch actual
    feeds. For testing we'll use a subclass so we can pass in the entries we
    want.
    """
    def __init__(self, entries):
        Notifier.__init__(self)
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
        self.triggerEntry = None
        self.triggerEvent = None

    def notify(self, event):
        self.notified = True
        self.triggerEntry = event.entry
        self.triggerEvent = event

class NotifierTests(unittest.TestCase):

    def testSimpleNotification(self):
        futureTime = datetime.now() + timedelta(minutes=10)
        self.__createEntry(futureTime)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)
        self.assertEqual(self.entry, self.observer.triggerEntry)

    def testNotificationBeyondThreshold(self):
        futureTime = datetime.now() + timedelta(minutes=DEFAULT_THRESHOLD,
            seconds=1)
        self.__createEntry(futureTime)
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)
        self.assertEqual(None, self.observer.triggerEntry)

    def testPastEvent(self):
        pastTime = datetime.now() - timedelta(minutes=30)
        self.__createEntry(pastTime)
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)
        self.assertEqual(None, self.observer.triggerEntry)

    def testEventConfirmed(self):
        eventTime = datetime.now() + timedelta(minutes=2)
        self.__createEntry(eventTime)
        self.notifier.check_for_notifications()
        self.assertTrue(self.observer.notified)
        self.assertEqual(self.entry, self.observer.triggerEntry)

        # Accept the event:
        self.observer.triggerEvent.accepted = True

        # Reset the observer and make sure he's not renotified:
        self.observer.notified = False
        self.notifier.check_for_notifications()
        self.assertFalse(self.observer.notified)

    def __createEntry(self, futureTime):
        self.entry = SingleOccurrenceEntry("fakeId", "Fake Title", "",
            datetime.now(), futureTime, 3600, "Gumdrop Alley")
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

