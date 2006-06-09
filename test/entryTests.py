import unittest
from datetime import datetime

import settestpath
from model import SingleOccurrenceEntry, RecurringEntry
from feedparser import FeedParser

# Sample data:
UPDATED = datetime(2006, 05, 26, 12, 00, 00)
TITLE = "Super Important Meeting"
DESCRIPTION = "In the future, there will be robots."
WHERE = "Main Boardroom"

class SingleOccurrenceEntryTests(unittest.TestCase):

    def testEventWithinEndtime(self):
        when = datetime(2015, 05, 23, 22, 0, 0)
        endDate = datetime(2020, 01, 01)

        distantEvent = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, UPDATED, when, 3600, WHERE)

        events = distantEvent.events(None, endDate)
        self.assertEquals(1, len(events))

        self.assertEquals(when, events[0].when)
        self.assertEquals(3600, events[0].duration)

    def testEventBeyondEndtime(self):
        when = datetime(2015, 05, 23, 22, 0, 0)
        endDate = datetime(2006, 01, 01)

        distantEvent = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, UPDATED, when, 3600, WHERE)

        self.assertEquals(0, len(distantEvent.events(None, endDate)))

    def testEventBeforeCurrentTime(self):
        when = datetime(1980, 05, 23, 22, 0, 0)
        endDate = datetime(2006, 05, 26)

        distantEvent = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, UPDATED, when, 3600, WHERE)

        self.assertEquals(0, len(distantEvent.events(None, endDate)))

# TODO: Single occurrence all day event.

class RecurringEntryTests(unittest.TestCase):

    def testQueryEndDateBeforeStartDate(self):
        standupMeeting = self.__getDailyRecurringEntry()
        startDate = datetime(2006, 06, 04)
        endDate = datetime(2006, 06, 03)
        self.assertEqual(0, len(standupMeeting.events(startDate, endDate)))

    def testQueryEndDateBeforeEntriesStartDate(self):
        standupMeeting = self.__getDailyRecurringEntry()
        # Event starts on May 18th 2006:
        startDate = datetime(2006, 02, 04)
        endDate = datetime(2006, 02, 05)
        self.assertEqual(0, len(standupMeeting.events(startDate, endDate)))

    def testDailyRecurringEntry(self):
        standupMeeting = self.__getDailyRecurringEntry()
        # Should return five occurences during a standard work week:
        startDate = datetime(2006, 06, 04)
        endDate = datetime(2006, 06, 10)
        events = standupMeeting.events(startDate, endDate)
        self.assertEqual(5, len(events))

    def __getDailyRecurringEntry(self):
        from sampledata import dailyRecurrence
        standupMeeting = RecurringEntry("fakeId", "Standup Meeting", "",
            WHERE, UPDATED, dailyRecurrence)
        self.assertEqual(1800, standupMeeting.duration)
        self.assertEqual(WHERE, standupMeeting.where)
        return standupMeeting

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SingleOccurrenceEntryTests))
    suite.addTest(unittest.makeSuite(RecurringEntryTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

