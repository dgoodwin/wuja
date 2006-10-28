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
import os
import os.path

from datetime import datetime, timedelta

import settestpath
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Event, Calendar, \
    BadDateRange
from sampledata import daily_recurrence, daily_recurrence_for_one_week, \
    weekly_recurrence_all_day, monthly_multi_day, wkst_recurrence
from utils import teardownDatabase, TEST_DB_FILE, TestCache

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

# TODO: Rename
# TODO: Stop hitting the filesystem:
class CacheTests(unittest.TestCase):
    __last_update = "whenever"

    def tearDown(self):
        teardownDatabase()

    def test_save(self):
        cal = Calendar(CAL_TITLE, CAL_URL, self.__last_update)
        mgr = TestCache(db=TEST_DB_FILE)
        mgr.save(cal)

        loaded_cal = mgr.load(cal.url)
        self.assertEqual(CAL_TITLE, loaded_cal.title)
        self.assertEqual(CAL_URL, loaded_cal.url)
        self.assertEqual(self.__last_update, loaded_cal.last_update)

    def test_empty_cache(self):
        cal = Calendar(CAL_TITLE, CAL_URL, self.__last_update)
        mgr = TestCache(db=TEST_DB_FILE)
        mgr.save(cal)
        self.assertEqual(1, len(mgr.load_all()))

        mgr.empty()
        self.assertEqual(0, len(mgr.load_all()))

    def test_save_calendar_id_already_exists(self):
        cal = Calendar(CAL_TITLE, CAL_URL, self.__last_update)
        mgr = TestCache(db=TEST_DB_FILE)
        mgr.save(cal)
        cal = Calendar("", CAL_URL, "")
        self.assertRaises(Exception, mgr.save, cal)
        mgr.close()

    def test_delete(self):
        cal = Calendar(CAL_TITLE, CAL_URL, self.__last_update)
        mgr = TestCache(db=TEST_DB_FILE)
        mgr.save(cal)
        mgr.delete(cal.url)
        self.assertEqual(0, len(mgr.load_all()))

    def test_delete_readd_without_close(self):
        cal = Calendar(CAL_TITLE, CAL_URL, self.__last_update)
        mgr = TestCache(db=TEST_DB_FILE)
        mgr.save(cal)
        mgr.delete(cal.url)
        mgr.save(cal)


class EventTests(unittest.TestCase):

    def setUp(self):
        self.cal = Calendar(FEED_TITLE, CAL_URL, "somedate")

    def test_event_key(self):
        time = datetime.now()
        entry = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION, REMIND,
            UPDATED, time, 3600, LOCATION, self.cal)
        event = Event(entry.time, entry)
        self.assertEqual(entry.entry_id + str(time),
            event.key)


class SingleOccurrenceEntryTests(unittest.TestCase):

    def setUp(self):
        self.cal = Calendar(FEED_TITLE, CAL_URL, "somedate")

    def test_event_within_end_time(self):
        time = datetime(2015, 05, 23, 22, 0, 0)
        end_date = datetime(2020, 01, 01)

        distant_event = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION,
            REMIND, UPDATED, time, 3600, LOCATION, self.cal)

        events = distant_event.get_events_starting_between(None, end_date)
        self.assertEquals(1, len(events))

        self.assertEquals(time, events[0].time)
        self.assertEquals(3600, events[0].entry.duration)

    def test_event_beyond_end_time(self):
        time = datetime(2015, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 01, 01)

        distant_event = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION,
            REMIND, UPDATED, time, 3600, LOCATION, self.cal)

        self.assertRaises(BadDateRange, distant_event
            .get_events_starting_between, None, end_date)

    def test_event_before_current_time(self):
        time = datetime(1980, 05, 23, 22, 0, 0)
        end_date = datetime(2006, 05, 26)

        distant_event = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, time, 3600, LOCATION, self.cal)

        self.assertRaises(BadDateRange, distant_event
            .get_events_starting_between, None, end_date)

    def test_time_equal_to_start_time(self):
        time = datetime(2006, 8, 1, 8, 42, 0)
        end_date = datetime(2007, 8, 1, 8, 42, 0)

        current_event = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, time, 812, LOCATION, self.cal)

        self.assertEqual(1, len(current_event.get_events_starting_between(
            time, end_date)))

    def test_time_equal_to_end_time(self):
        start_date = datetime(2006, 8, 1, 8, 42, 0)
        end_date = datetime(2007, 8, 1, 8, 42, 0)

        current_event = SingleOccurrenceEntry("fakeId", TITLE,
            DESCRIPTION, REMIND, UPDATED, end_date, 812, LOCATION, self.cal)

        self.assertEqual(1, len(current_event.get_events_starting_between(
            start_date, end_date)))

    def test_occurring_on_with_all_day_event(self):
        """
        Test an all-day event is returned for a call to occuring on.
        """
        time = datetime(2006, 10, 28)
        all_day = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION,
            REMIND, UPDATED, time, 86400, LOCATION, self.cal)

        events = all_day.get_events_occurring_on(time)
        self.assertEquals(1, len(events))

    def test_occurring_on_all_day_event_yesterday(self):
        """
        Test that an all day event is not returned when querying the next
        day.
        """
        time = datetime(2006, 10, 28)
        all_day = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION,
            REMIND, UPDATED, time, 86400, LOCATION, self.cal)

        events = all_day.get_events_occurring_on(time + timedelta(days=1))
        self.assertEquals(0, len(events))

    def test_occurring_on_all_day_event_tomorrow(self):
        """
        Test that an all day event is not returned when querying the previous
        day.
        """
        time = datetime(2006, 10, 28)
        all_day = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION,
            REMIND, UPDATED, time, 86400, LOCATION, self.cal)

        events = all_day.get_events_occurring_on(time - timedelta(days=1))
        self.assertEquals(0, len(events))

    def test_occurring_on_with_multi_day_event(self):
        """
        Test a multi-day event that starts before and ends after the date
        queried.
        """
        query_date = datetime(2006, 10, 26)
        event_start = datetime(2006, 10, 20)
        event_duration = 60 * 60 * 24 * 14 # two weeks

        vacation = SingleOccurrenceEntry("fakeId", TITLE, DESCRIPTION,
            REMIND, UPDATED, event_start, event_duration, LOCATION, self.cal)

        events = vacation.get_events_occurring_on(query_date)
        self.assertEquals(1, len(events))


class RecurringEntryTests(unittest.TestCase):

    def setUp(self):
        self.cal = Calendar(FEED_TITLE, CAL_URL, "somedate")

    def __get_daily_recurring_entry(self):
        standup_meeting = RecurringEntry("fakeId", "Standup Meeting", "",
            REMIND, LOCATION, UPDATED, daily_recurrence, self.cal)
        self.assertEqual(1800, standup_meeting.duration)
        self.assertEqual(LOCATION, standup_meeting.location)
        return standup_meeting

    def test_query_end_date_before_start_date(self):
        standup_meeting = self.__get_daily_recurring_entry()
        start_date = datetime(2006, 06, 04)
        end_date = datetime(2006, 06, 03)
        self.assertRaises(BadDateRange, standup_meeting
            .get_events_starting_between, start_date, end_date)

    def test_query_end_date_before_entries_start_date(self):
        standup_meeting = self.__get_daily_recurring_entry()
        # Event starts on May 18th 2006:
        start_date = datetime(2006, 02, 04)
        end_date = datetime(2006, 02, 05)
        self.assertEqual(0, len(standup_meeting.get_events_starting_between(
            start_date, end_date)))

    def test_daily_recurring_entry(self):
        standup_meeting = self.__get_daily_recurring_entry()
        # Should return five occurences during a standard work week:
        start_date = datetime(2006, 06, 04)
        end_date = datetime(2006, 06, 10)
        events = standup_meeting.get_events_starting_between(start_date,
            end_date)
        self.assertEqual(5, len(events))

    def test_daily_recurring_entry_for_one_week(self):
        daily_for_one_week = RecurringEntry("fakeId", "Daily For One Week",
            "", REMIND, LOCATION, UPDATED, daily_recurrence_for_one_week,
            self.cal)
        self.assertEqual(3600, daily_for_one_week.duration)
        self.assertEqual(LOCATION, daily_for_one_week.location)
        start_date = datetime(2006, 6, 1)
        end_date = datetime(2006, 6, 30)
        events = daily_for_one_week.get_events_starting_between(start_date,
            end_date)
        self.assertEquals(5, len(events))

    def test_weekly_all_day_recurrence(self):
        weekly_all_day = RecurringEntry("fakeId", "Weekly All Day", "",
            REMIND, LOCATION, UPDATED, weekly_recurrence_all_day, self.cal)
        self.assertEqual(86400, weekly_all_day.duration)

        # Event starts on June 5th 2006
        start_date = datetime(2006, 5, 28)
        end_date = datetime(2006, 6, 30)
        events = weekly_all_day.get_events_starting_between(start_date,
            end_date)
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
        entry = RecurringEntry("fakeId", "Wkst Entry", "", REMIND, LOCATION,
            UPDATED, wkst_recurrence, self.cal)

    def test_weekly_all_day_occuring_today(self):
        """
        Test an all-day event is returned for a call to occuring on.
        """
        weekly_all_day = RecurringEntry("fakeId", "Weekly All Day", "",
            REMIND, LOCATION, UPDATED, weekly_recurrence_all_day, self.cal)

        time = datetime(2006, 6, 5)
        events = weekly_all_day.get_events_occurring_on(time)
        self.assertEquals(1, len(events))

    def test_weekly_all_day_occurring_yesterday(self):
        weekly_all_day = RecurringEntry("fakeId", "Weekly All Day", "",
            REMIND, LOCATION, UPDATED, weekly_recurrence_all_day, self.cal)

        time = datetime(2006, 6, 5)

        events = weekly_all_day.get_events_occurring_on(time +
            timedelta(days=1))
        self.assertEquals(0, len(events))

    def test_weekly_all_day_occurring_tomorrow(self):
        weekly_all_day = RecurringEntry("fakeId", "Weekly All Day", "",
            REMIND, LOCATION, UPDATED, weekly_recurrence_all_day, self.cal)

        time = datetime(2006, 6, 5)

        events = weekly_all_day.get_events_occurring_on(time -
            timedelta(days=1))
        self.assertEquals(0, len(events))

    def __multi_day_tester(self, query_date, expected):
        # monthly_multi_day = 25-27th of every month (starting Oct 06):
        entry = RecurringEntry("fakeId", "Montly Multi-Day", "",
            REMIND, LOCATION, UPDATED, monthly_multi_day, self.cal)
        events = entry.get_events_occurring_on(query_date)
        self.assertEquals(expected, len(events))

    def test_monthly_multi_day_over_query_date(self):
        self.__multi_day_tester(datetime(2006, 10, 26), 1)

    def test_monthly_multi_day_start_of_query_date(self):
        self.__multi_day_tester(datetime(2006, 10, 25), 1)

    def test_monthly_multi_day_end_of_query_date(self):
        self.__multi_day_tester(datetime(2006, 10, 27), 1)

    def test_monthly_multi_day_misses_query_date(self):
        self.__multi_day_tester(datetime(2006, 10, 24), 0)

    def test_monthly_multi_day_misses_query_date_again(self):
        self.__multi_day_tester(datetime(2006, 10, 28), 0)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheTests))
    suite.addTest(unittest.makeSuite(SingleOccurrenceEntryTests))
    suite.addTest(unittest.makeSuite(RecurringEntryTests))
    suite.addTest(unittest.makeSuite(EventTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
