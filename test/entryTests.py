import unittest
import settestpath

from model import SingleOccurrenceEntry

from datetime import datetime

class EntryTests(unittest.TestCase):

    def testSingleDistantEvent(self):
        updatedDate = datetime(2005, 05, 26, 12, 00, 00)
        when = datetime(2015, 05, 23, 22, 0, 0)
        distantEvent = SingleOccurrenceEntry("fakeId", "Distant Event",
            "Description.", updatedDate, when, 3600, "Main Boardroom")
        self.assertEquals("fakeId", distantEvent.id)

        # Distant Event is in the year 2015, make sure we get it:
        endDate = datetime(2020, 01, 01)

        events = distantEvent.events(endDate)
        self.assertEquals(1, len(events))

        self.assertEquals(when, events[0].when)
        self.assertEquals(60*60, events[0].duration)

# TODO: Single occurrence all day event.

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EntryTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

