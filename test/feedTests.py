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

""" Tests for feeds. """

__revision__ = "$Revision$"

import unittest
import settestpath

from datetime import datetime

from wuja.feed import parse_timestamp, build_calendar
from samplefeed import xml
from dateutil.tz import gettz

FEED_URL = "http://whatever.com/feedurl"
FEED_TITLE = "Wuja Testing Calendar"
FEED_LAST_UPDATE = "Doesn't matter."
CAL_TZ = "America/Halifax"
TZ = gettz(CAL_TZ)

class FeedSourceTests(unittest.TestCase):

    def test_simple_entry(self):
        cal = build_calendar(xml, FEED_LAST_UPDATE, FEED_URL)
        distant_event = find_entries(cal.entries, "Distant Event")[0]
        self.assertTrue(distant_event != None)

    def test_timestamp_parsing(self):
        timestamp = "2006-05-18T15:24:41.000Z"
        date = parse_timestamp(timestamp, TZ)
        self.assertEquals(2006, date.year)
        self.assertEquals(15, date.hour)
        self.assertEquals(24, date.minute)
        self.assertEquals(41, date.second)

    def test_recurring_exception_changed_time(self):
        cal = build_calendar(xml, FEED_LAST_UPDATE, FEED_URL)
        entries = find_entries(cal.entries, "Recurring With Exception")
        self.assertEqual(2, len(entries))

        # Find the parent event:
        original_event = None
        exception_event = None
        if len(entries[0].exceptions) > 0:
            self.assertEqual(0, len(entries[1].exceptions))
            original_event = entries[0]
            exception_event = entries[1]
        else:
            self.assertEqual(1, len(entries[1].exceptions))
            original_event = entries[1]
            exception_event = entries[0]

        # Check that only 4 of the 5 events are returned for the week:
        start = datetime(2006, 11, 20, tzinfo=TZ)
        end = datetime(2006, 11, 26, tzinfo=TZ)
        events = original_event.get_events_starting_between(start, end)
        self.assertEqual(4, len(events))

    def test_recurrence_cancellation_exception(self):
        cal = build_calendar(xml, FEED_LAST_UPDATE, FEED_URL)
        entries = find_entries(cal.entries, "Recurring With Cancellation")
        self.assertEquals(1, len(entries))

        e = entries[0]
        self.assertEquals(1, len(e.exceptions))

        # Check that only 4 events are returned for the week:
        start = datetime(2007, 1, 1, tzinfo=TZ)
        end = datetime(2007, 1, 8, tzinfo=TZ)
        events = e.get_events_starting_between(start, end)
        self.assertEqual(4, len(events))

        events = e.get_events_occurring_on(datetime(2007, 1, 3, tzinfo=TZ))
        self.assertEqual(0, len(events))



def find_entries(entries, title):
    """ Returns the entries with the given title. """
    found_entries = []
    for entry in entries:
        if entry.title == title:
            found_entries.append(entry)
    if len(found_entries) == 0:
        raise Exception('Unable to find calendar event: "' + title + '"')
    return found_entries

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeedSourceTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

