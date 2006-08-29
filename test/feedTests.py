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

from wuja.feed import FeedSource, parse_timestamp, build_calendar
from samplefeed import xml

FEED_URL = "http://whatever.com/feedurl"
FEED_TITLE = "Wuja Testing Calendar"
FEED_LAST_UPDATE = "Doesn't matter."

class FeedSourceTests(unittest.TestCase):

    def test_simple_entry(self):
        cal = build_calendar(xml, FEED_LAST_UPDATE, FEED_URL)
        distant_event = find_entry(cal.entries, "Distant Event")
        self.assertTrue(distant_event != None)

    def test_timestamp_parsing(self):
        timestamp = "2006-05-18T15:24:41.000Z"
        date = parse_timestamp(timestamp)
        self.assertEquals(2006, date.year)
        self.assertEquals(15, date.hour)
        self.assertEquals(24, date.minute)
        self.assertEquals(41, date.second)

def find_entry(entries, title):
    for entry in entries:
        if entry.title == title:
            return entry
    raise Exception('Unable to find calendar event: "' + title + '"')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeedSourceTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

