import unittest
from datetime import datetime

import settestpath
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Event
from wuja.feedparser import FeedParser
from sampledata import daily_recurrence, daily_recurrence_for_one_week, \
    weekly_recurrence_all_day

# Sample data:
UPDATED = datetime(2006, 05, 26, 12, 00, 00)
TITLE = "Super Important Meeting"
DESCRIPTION = "In the future, there will be robots."
WHERE = "Main Boardroom"
REMIND = 10

class SingleOccurrenceEntryTests(unittest.TestCase):

    def test_event_within_end_time(self):
        when = datetime(2015, 05, 23, 22, 0, 0)
        end_date = datetime(2020, 01, 01)

        distant_event = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, when, 3600, WHERE)

        events = distant_event.events(None, end_date)
        self.assertEquals(1, len(events))

        self.assertEquals(when, events[0].when)
        self.assertEquals(3600, events[0].entry.duration)

    def testEventBeyondEndtime(self):
        when = datetime(2015, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 01, 01)

        distant_event = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, when, 3600, WHERE)

        self.assertEquals(0, len(distant_event.events(None, end_date)))

    def testEventBeforeCurrentTime(self):
        when = datetime(1980, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 05, 26)

        distant_event = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, when, 3600, WHERE)

        self.assertEquals(0, len(distant_event.events(None, end_date)))

class RecurringEntryTests(unittest.TestCase):

    def __get_daily_recurring_entry(self):
        standup_meeting = RecurringEntry("fakeId", "Standup Meeting", "",
            REMIND, WHERE, UPDATED, daily_recurrence)
        self.assertEqual(1800, standup_meeting.duration)
        self.assertEqual(WHERE, standup_meeting.where)
        return standup_meeting

    def test_query_end_date_before_start_date(self):
        standup_meeting = self.__get_daily_recurring_entry()
        start_date = datetime(2006, 06, 04)
        end_date = datetime(2006, 06, 03)
        self.assertEqual(0, len(standup_meeting.events(start_date, end_date)))

    def test_query_end_date_before_entries_start_date(self):
        standup_meeting = self.__get_daily_recurring_entry()
        # Event starts on May 18th 2006:
        start_date = datetime(2006, 02, 04)
        end_date = datetime(2006, 02, 05)
        self.assertEqual(0, len(standup_meeting.events(start_date, end_date)))

    def test_daily_recurring_entry(self):
        standup_meeting = self.__get_daily_recurring_entry()
        # Should return five occurences during a standard work week:
        start_date = datetime(2006, 06, 04)
        end_date = datetime(2006, 06, 10)
        events = standup_meeting.events(start_date, end_date)
        self.assertEqual(5, len(events))

    def test_daily_recurring_entry_for_one_week(self):
        daily_for_one_week = RecurringEntry("fakeId", "Daily For One Week", "",
            REMIND, WHERE, UPDATED, daily_recurrence_for_one_week)
        self.assertEqual(3600, daily_for_one_week.duration)
        self.assertEqual(WHERE, daily_for_one_week.where)
        start_date = datetime(2006, 6, 1)
        end_date = datetime(2006, 6, 30)
        events = daily_for_one_week.events(start_date, end_date)
        self.assertEquals(5, len(events))

    def test_weekly_all_day_recurrence(self):
        weekly_all_day = RecurringEntry("fakeId", "Weekly All Day", "",
            REMIND, WHERE, UPDATED, weekly_recurrence_all_day)
        self.assertEqual(None, weekly_all_day.duration)

        # Event starts on June 5th 2006
        start_date = datetime(2006, 5, 28)
        end_date = datetime(2006, 6, 30)
        events = weekly_all_day.events(start_date, end_date)
        self.assertEquals(4, len(events))

        self.assertEquals(2006, events[0].when.year)
        self.assertEquals(6, events[0].when.month)
        self.assertEquals(5, events[0].when.day)


        self.assertEquals(6, events[1].when.month)
        self.assertEquals(12, events[1].when.day)

        self.assertEquals(6, events[2].when.month)
        self.assertEquals(19, events[2].when.day)

        self.assertEquals(6, events[3].when.month)
        self.assertEquals(26, events[3].when.day)

class EventTests(unittest.TestCase):

    def test_event_key(self):
        when = datetime.now()
        entry = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, when, 3600, WHERE)
        event = Event(entry.when, entry)
        self.assertEqual(entry.entry_id + str(when), event.key)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SingleOccurrenceEntryTests))
    suite.addTest(unittest.makeSuite(RecurringEntryTests))
    suite.addTest(unittest.makeSuite(EventTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

