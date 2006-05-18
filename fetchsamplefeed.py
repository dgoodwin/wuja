#!/usr/bin/env python
#
# Fetch a sample feed from an actual test calendar. Stored in an XML file, ideally
# used as a string variable for parsing tests rather than being read from disk.

import urllib2

# Location of the Wuja Testing Calendar:
feedUrl = \
"""
http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps@group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full
"""

feed = urllib2.urlopen(feedUrl).read()
outputFile = open('samplefeed.xml', 'w')
outputFile.write(feed)
