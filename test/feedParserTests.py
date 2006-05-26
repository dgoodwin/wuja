import unittest
import settestpath

from feedparser import FeedParser, parseTimestamp
from datetime import datetime

from sampledata import xml

class ParsingTests(unittest.TestCase):

    # One entry, no recurrence:
    def testSimpleEntry(self):
        feedParser = FeedParser(xml)
        entries = feedParser.entries()

        # Distant Event is in the year 3000, make sure we get it:
        endDate = datetime(3001, 01, 01)

        distantEvent = findEntry(entries, "Distant Event")
        self.assertTrue(distantEvent != None)
        events = distantEvent.events(endDate)
        self.assertEquals(1, len(events))
        expectedWhen = datetime(3000, 05, 23, 22, 0, 0)
        # "3000-05-23T22:00:00.000-03:00" endTime="3000-05-23T23:00:00.000-03:00"
        self.assertEquals(expectedWhen, events[0].when)
        self.assertEquals(60*60, events[0].duration)

    # Recurring entry, no exceptions:
    #def testRecurringEntry(self):
    #    feedParser = FeedParser(xml)
    #    entries = feedParser.entries()

    #    standupMeeting = findEntry(entries, "Standup Meeting")
    #    self.assertTrue(standupMeeting != None)
    #    self.assertEquals(2006, standupMeeting.updated.year)
    #    self.assertEquals(5, standupMeeting.updated.month)
    #    self.assertEquals(18, standupMeeting.updated.day)
    #    self.assertTrue(len(standupMeeting.recurrence) > 0)

    def testTimestampParsing(self):
        timestamp = "2006-05-18T15:24:41.000Z"
        date = parseTimestamp(timestamp)
        self.assertEquals(2006, date.year)
        self.assertEquals(15, date.hour)
        self.assertEquals(24, date.minute)
        self.assertEquals(41, date.second)

def findEntry(entries, title):
    for entry in entries:
        if entry.title == title:
            return entry
    raise Exception('Unable to find calendar event: "' + title + '"')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ParsingTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

