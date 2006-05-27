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

        distantEvent = findEntry(entries, "Distant Event")
        self.assertTrue(distantEvent != None)

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

