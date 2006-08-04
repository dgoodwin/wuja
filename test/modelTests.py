#   Wuja - Google Calendar (tm) notifications for the GNOME desktop.
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" Tests for the wuja.model module. """

import unittest
import sqlobject

from datetime import datetime

import settestpath
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Event, Calendar, \
    BadDateRange
from sampledata import daily_recurrence, daily_recurrence_for_one_week, \
    weekly_recurrence_all_day, wkst_recurrence
from utils import setupDatabase, teardownDatabase

# Sample data:
UPDATED = str(datetime(2006, 05, 26, 12, 00, 00))
CAL_TITLE = "Test Calendar"
CAL_URL = "http://fakecalurl"
TITLE = "Super Important Meeting"
RECURRING_TITLE = "Super Important Every Day Meeting"
DESCRIPTION = "In the future, there will be robots."
LOCATION = "Main Boardroom"
REMIND = 10
FEED_TITLE = "fakefeed"

class CalendarTests(unittest.TestCase):
    __last_update = "whenever"

    def setUp(self):
        setupDatabase()

    def tearDown(self):
        teardownDatabase()

    def test_simple_calendar(self):
        cal = Calendar(title=CAL_TITLE, last_update=self.__last_update,
            url=CAL_URL)
        cal = Calendar.get(cal.id)
        self.assertEqual(CAL_TITLE, cal.title)
        self.assertEqual(self.__last_update, cal.last_update)
        self.assertEqual(0, len(cal.entries))

    def test_calendar_with_entries(self):
        cal = Calendar(title=CAL_TITLE, last_update=self.__last_update,
            url=CAL_URL)
        self.assertEqual(0, len(cal.entries))

        single_entry = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=datetime.now(), duration=3600, location=LOCATION, calendar=cal)
        recur_entry = RecurringEntry(entry_id="fakeId",
            title=RECURRING_TITLE, description="",
            reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=weekly_recurrence_all_day, calendar=cal)

        cal = cal.get(cal.id)
        self.assertEqual(2, len(cal.entries))

    def test_delete_calendar(self):
        cal = Calendar(title=CAL_TITLE, last_update=self.__last_update,
            url=CAL_URL)
        single_entry = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=datetime.now(), duration=3600, location=LOCATION, calendar=cal)
        recur_entry = RecurringEntry(entry_id="fakeId",
            title=RECURRING_TITLE, description="",
            reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=weekly_recurrence_all_day, calendar=cal)

        self.assertEqual(1, len(list(Calendar.select())))
        self.assertEqual(2, len(cal.entries))
        self.assertEqual(1, len(list(SingleOccurrenceEntry.select())))
        self.assertEqual(1, len(list(RecurringEntry.select())))

        cal.destroySelf()
        self.assertEqual(0, len(list(Calendar.select())))
        self.assertEqual(0, len(list(SingleOccurrenceEntry.select())))
        self.assertEqual(0, len(list(RecurringEntry.select())))


class SingleOccurrenceEntryTests(unittest.TestCase):

    def setUp(self):
        setupDatabase()
        self.cal = Calendar(title=FEED_TITLE, last_update="somedate",
            url=CAL_URL)

    def tearDown(self):
        teardownDatabase()

    def test_event_within_end_time(self):
        time = datetime(2015, 05, 23, 22, 0, 0)
        end_date = datetime(2020, 01, 01)

        distant_event = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=time, duration=3600, location=LOCATION, calendar=self.cal)

        events = distant_event.get_events(None, end_date)
        self.assertEquals(1, len(events))

        self.assertEquals(time, events[0].time)
        self.assertEquals(3600, events[0].entry.duration)

    def test_event_beyond_end_time(self):
        time = datetime(2015, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 01, 01)

        distant_event = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=time, duration=3600, location=LOCATION, calendar=self.cal)

        self.assertRaises(BadDateRange, distant_event.get_events, None,
            end_date)

    def test_event_before_current_time(self):
        time = datetime(1980, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 05, 26)

        distant_event = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=time, duration=3600, location=LOCATION, calendar=self.cal)

        self.assertRaises(BadDateRange, distant_event.get_events, None,
            end_date)

    def test_time_equal_to_start_time(self):
        time = datetime(2006, 8, 1, 8, 42, 0)
        end_date = datetime(2007, 8, 1, 8, 42, 0)

        current_event = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=time, duration=812, location=LOCATION, calendar=self.cal)

        self.assertEqual(1, len(current_event.get_events(time, end_date)))

    def test_time_equal_to_end_time(self):
        start_date = datetime(2006, 8, 1, 8, 42, 0)
        end_date = datetime(2007, 8, 1, 8, 42, 0)

        current_event = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=end_date, duration=812, location=LOCATION, calendar=self.cal)

        self.assertEqual(1, len(current_event.get_events(start_date, end_date)))

    def test_event_lookup(self):
        # Create an entry:
        time = datetime(1980, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 05, 26)
        entry = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND,
            updated=UPDATED, time=time, duration=3600, location=LOCATION,
            calendar=self.cal)
        # Look it up:
        lookup = SingleOccurrenceEntry.get(entry.id)
        self.assertEqual(TITLE, lookup.title)
        self.assertEqual("fakeId", lookup.entry_id)
        self.assertEqual(DESCRIPTION, lookup.description)
        self.assertEqual(REMIND, lookup.reminder)
        self.assertEqual(UPDATED, lookup.updated)
        self.assertEqual(time, lookup.time)
        self.assertEqual(3600, lookup.duration)
        self.assertEqual(LOCATION, lookup.location)
        self.assertEqual(FEED_TITLE, lookup.calendar.title)

    def test_search_for_all(self):
        all_entries = list(SingleOccurrenceEntry.select())
        self.assertEqual(0, len(all_entries))

class RecurringEntryTests(unittest.TestCase):

    def setUp(self):
        setupDatabase()
        self.cal = Calendar(title=FEED_TITLE, last_update="somedate",
            url=CAL_URL)

    def tearDown(self):
        teardownDatabase()

    def __get_daily_recurring_entry(self):
        standup_meeting = RecurringEntry(entry_id="fakeId",
            title="Standup Meeting", description="",
            reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=daily_recurrence, calendar=self.cal)
        self.assertEqual(1800, standup_meeting.duration)
        self.assertEqual(LOCATION, standup_meeting.location)
        return standup_meeting

    def test_query_end_date_before_start_date(self):
        standup_meeting = self.__get_daily_recurring_entry()
        start_date = datetime(2006, 06, 04)
        end_date = datetime(2006, 06, 03)
        self.assertRaises(BadDateRange, standup_meeting.get_events, start_date,
            end_date)

    def test_query_end_date_before_entries_start_date(self):
        standup_meeting = self.__get_daily_recurring_entry()
        # Event starts on May 18th 2006:
        start_date = datetime(2006, 02, 04)
        end_date = datetime(2006, 02, 05)
        self.assertEqual(0, len(standup_meeting.get_events(start_date,
            end_date)))

    def test_daily_recurring_entry(self):
        standup_meeting = self.__get_daily_recurring_entry()
        # Should return five occurences during a standard work week:
        start_date = datetime(2006, 06, 04)
        end_date = datetime(2006, 06, 10)
        events = standup_meeting.get_events(start_date, end_date)
        self.assertEqual(5, len(events))

    def test_daily_recurring_entry_for_one_week(self):
        daily_for_one_week = RecurringEntry(entry_id="fakeId",
            title="Daily For One Week", description="",
            reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=daily_recurrence_for_one_week, calendar=self.cal)
        self.assertEqual(3600, daily_for_one_week.duration)
        self.assertEqual(LOCATION, daily_for_one_week.location)
        start_date = datetime(2006, 6, 1)
        end_date = datetime(2006, 6, 30)
        events = daily_for_one_week.get_events(start_date, end_date)
        self.assertEquals(5, len(events))

    def test_weekly_all_day_recurrence(self):
        weekly_all_day = RecurringEntry(entry_id="fakeId",
            title="Weekly All Day", description="",
            reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=weekly_recurrence_all_day, calendar=self.cal)
        self.assertEqual(None, weekly_all_day.duration)

        # Event starts on June 5th 2006
        start_date = datetime(2006, 5, 28)
        end_date = datetime(2006, 6, 30)
        events = weekly_all_day.get_events(start_date, end_date)
        self.assertEquals(4, len(events))

        self.assertEquals(2006, events[0].time.year)
        self.assertEquals(6, events[0].time.month)
        self.assertEquals(5, events[0].time.day)


        self.assertEquals(6, events[1].time.month)
        self.assertEquals(12, events[1].time.day)

        self.assertEquals(6, events[2].time.month)
        self.assertEquals(19, events[2].time.day)

        self.assertEquals(6, events[3].time.month)
        self.assertEquals(26, events[3].time.day)

    def test_recurrence_wkst(self):
        """ Test a recurrence with a wkst parameter. (errors parsing
        these at one point in time)
        """
        entry = RecurringEntry(entry_id="fakeId", title="Wkst Entry",
            description="", reminder=REMIND, location=LOCATION, updated=UPDATED,
            recurrence=wkst_recurrence, calendar=self.cal)

class EventTests(unittest.TestCase):

    def setUp(self):
        setupDatabase()
        self.cal = Calendar(title=FEED_TITLE, last_update="somedate",
            url=CAL_URL)

    def tearDown(self):
        teardownDatabase()

    def test_event_key(self):
        time = datetime.now()
        entry = SingleOccurrenceEntry(entry_id="fakeId", title=TITLE,
            description=DESCRIPTION, reminder=REMIND, updated=UPDATED,
            time=time, duration=3600, location=LOCATION, calendar=self.cal)
        event = Event(entry.time, entry)
        self.assertEqual(entry.entry_id + time.strftime("%Y-%m-%d %H:%M:%S"),
            event.key)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CalendarTests))
    suite.addTest(unittest.makeSuite(SingleOccurrenceEntryTests))
    suite.addTest(unittest.makeSuite(RecurringEntryTests))
    suite.addTest(unittest.makeSuite(EventTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
