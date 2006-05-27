import unittest
from datetime import datetime

import settestpath
from model import SingleOccurrenceEntry


# Sample data:
UPDATED = datetime(2006, 05, 26, 12, 00, 00)
TITLE = "Super Important Meeting"
DESCRIPTION = "In the future, there will be robots."

class EntryTests(unittest.TestCase):

    def testEventWithinEndtime(self):
        when = datetime(2015, 05, 23, 22, 0, 0)
        endDate = datetime(2020, 01, 01)

        distantEvent = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, UPDATED, when, 3600, "Main Boardroom")

        events = distantEvent.events(endDate)
        self.assertEquals(1, len(events))

        self.assertEquals(when, events[0].when)
        self.assertEquals(3600, events[0].duration)

    def testEventBeyondEndtime(self):
        when = datetime(2015, 05, 23, 22, 0, 0)
        endDate = datetime(2006, 01, 01)

        distantEvent = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, UPDATED, when, 3600, "Main Boardroom")

        self.assertEquals(0, len(distantEvent.events(endDate)))

    def testEventBeforeCurrentTime(self):
        when = datetime(1980, 05, 23, 22, 0, 0)
        endDate = datetime(2006, 05, 26)

        distantEvent = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, UPDATED, when, 3600, "Main Boardroom")

        self.assertEquals(0, len(distantEvent.events(endDate)))

# TODO: Single occurrence all day event.

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EntryTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

