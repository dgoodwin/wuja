import unittest
import datetime

import settestpath

from notifier import Notifier
from model import SingleOccurrenceEntry

class TestNotifier(Notifier):
    """
    Notifier class talks directly with Google's servers to fetch actual
    feeds. For testing we'll use a subclass so we can pass in the entries we
    want.
    """
    def __init__(self, entries):
        Notifier.__init__(self)
        self.calendarEntries = entries
        self.update()
        self.updateEvents()

    def update(self):
        """
        Override the parent method that actually updates feeds from Google.
        We were provided a list of entries and there's no need to update them.
        """
        pass

class TestObserver:
    def __init__(self):
        self.notified = False

    def notify(self):
        self.notified = True

class NotifierTests(unittest.TestCase):

    def testSimpleNotification(self):
        # Create entry for less than 60 seconds in the future:
        futureTime = datetime.datetime.now() + datetime.timedelta(seconds=55)
        self.__createEntry(futureTime)
        self.notifier.checkForNotifications()
        self.assertTrue(self.observer.notified)

    def testNotificationBeyondThreshold(self):
        futureTime = datetime.datetime.now() + datetime.timedelta(seconds=61)
        self.__createEntry(futureTime)
        self.notifier.checkForNotifications()
        self.assertFalse(self.observer.notified)

    def __createEntry(self, futureTime):
        entry = SingleOccurrenceEntry("fakeId", "Fake Title", "",
            datetime.datetime.now(), futureTime, 3600, "Gumdrop Alley")
        self.notifier = TestNotifier([entry])
        self.observer = TestObserver()
        self.notifier.attach(self.observer)
        self.assertFalse(self.observer.notified)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NotifierTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

