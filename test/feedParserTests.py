import unittest
import settestpath

from feedparser import FeedParser, parseTimestamp
from datetime import datetime

from sampledata import xml

class ParsingTests(unittest.TestCase):

    # One event, no recurrence:
    def testSimpleEvent(self):
        feedParser = FeedParser(xml)
        events = feedParser.events()

        standupMeeting = findEvent

    # Recurring event, no exceptions:
    def testRecurringEvent(self):
        feedParser = FeedParser(xml)
        events = feedParser.events()

        standupMeeting = findEvent(events, "Standup Meeting")
        self.assertTrue(standupMeeting != None)
        self.assertEquals(2006, standupMeeting.updated.year)
        self.assertEquals(5, standupMeeting.updated.month)
        self.assertEquals(18, standupMeeting.updated.day)
        self.assertTrue(len(standupMeeting.recurrence) > 0)

    def testTimestampParsing(self):
        timestamp = "2006-05-18T15:24:41.000Z"
        date = parseTimestamp(timestamp)
        self.assertEquals(2006, date.year)

def findEvent(events, title):
    for event in events:
        if event.title == title:
            return event
    raise Exception('Unable to find calendar event: "' + title + '"')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ParsingTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

