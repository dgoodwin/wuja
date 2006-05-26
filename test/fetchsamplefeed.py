#!/usr/bin/env python
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
outputFile = open('sampledata.py', 'w')
outputFile.write("xml = \"\"\"" + feed + "\"\"\"")
