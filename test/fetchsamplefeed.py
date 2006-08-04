#!/usr/bin/env python
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

#
# Fetch the Google Feed for the Wuja Testing Calendar, and save it to
# sampledata.py so the unit tests can import it easily.
#
# Run from the test directory only, otherwise your sampledata.py will be in the
# wrong place. Only needs to happen when something in the feed changes,
# baseline feed will be comitted to svn. (and you should recommit when you make
# a change and rerun this script.)

import urllib2

# Location of the Wuja Testing Calendar:
feedUrl = \
"""
http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps@group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full
"""

feed = urllib2.urlopen(feedUrl).read()
outputFile = open('samplefeed.py', 'w')
outputFile.write("xml = \"\"\"" + feed + "\"\"\"")
