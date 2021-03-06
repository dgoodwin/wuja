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

""" Components for parsing the XML returned by Google's feeds. """

__revision__ = "$Revision$"

import time
import urllib2

from datetime import datetime

# Element tree was moved into Python 2.5 as _elementtree, support both:
try:
    from _elementtree import ElementTree, XML
except ImportError:
    from elementtree import ElementTree, XML

from logging import getLogger

from wuja.model import SingleOccurrenceEntry
from wuja.model import RecurringEntry
from wuja.model import Calendar
from dateutil.tz import gettz

logger = getLogger("feed")

STATUS_CANCELLED = "http://schemas.google.com/g/2005#event.canceled"

class FeedOpenError(Exception):
    pass



class FeedSource:
    """ Builds feeds objects given a URL. """

    def get_calendar(self, url):
        """ Return the calendar for the given URL. """
        last_update = self.get_feed_last_update(url)
        return build_calendar(self._get_feed_xml(url), url, last_update)

    def get_feed_last_update(self, url):
        """ Fetch the last updated time for the given feed URL. """
        try:
            url_file = urllib2.urlopen(url)
        except urllib2.URLError, e:
            raise FeedOpenError, str(e)
        return url_file.headers['last-modified']

    def _get_feed_xml(self, url):
        """ Append any custom parameters to the url and fetch the full
        XML source for the feed from Google's servers.
        """
        return urllib2.urlopen(url + "?max-results=10000").read()



def build_calendar(xml, url, last_update):
    __root_node = XML(xml)
    title = None
    timezone = None

    # Scan once just to gather data so we can create a calendar object:
    for elem in __root_node.getchildren():
        if parse_tag(elem.tag) == "title":
            title = elem.text
        elif parse_tag(elem.tag) == 'timezone':
            timezone = elem.attrib['value']
    logger.debug("Building calendar: " + title)
    cal = Calendar(title=title, last_update=last_update, url=url,
        timezone=timezone)

    # Maintain a running list of exceptions, map entry id to list of
    # exceptions:
    exceptions = {}
    for elem in __root_node.getchildren():
        if parse_tag(elem.tag) == "entry":
            create_entry(elem, cal, exceptions)

    # Tack on the exceptions:
    for entry in cal.entries:
        if exceptions.has_key(entry.entry_id):
            entry.exceptions.extend(exceptions[entry.entry_id])

    return cal

def parse_tag(original_tag):
    """ Element Tree tags show up with a {url} prefix. """
    return original_tag.split("}")[1]

def parse_timestamp(timestamp, tz):
    """ Convert internet timestamp (RFC 3339) into a Python datetime
    object.
    """
    date_str = None
    hour = None
    minute = None
    second = None
    # Single occurrence all day events return with only a date:
    if timestamp.count('T') > 0:
        date_str, time_str = timestamp.split('T')
        time_str = time_str.split('.')[0]
        hour, minute, second = time_str.split(':')
    else:
        date_str = timestamp
        hour, minute, second = 0, 0, 0

    year, month, day = date_str.split('-')
    return datetime(int(year), int(month), int(day), int(hour), int(minute),
        int(second), tzinfo=tz)

def create_entry(elem, cal, exceptions):
    """ Parses calender entry XML into an Entry object. """
    entry_id = None
    title = None
    description = None
    updated = None
    recurrence = None
    when = None
    where = None
    duration = None
    reminder = None

    cancelled = False

    tz = gettz(cal.timezone)

    for node in elem.getchildren():
        if parse_tag(node.tag) == 'id':
            entry_id = node.text

        elif parse_tag(node.tag) == 'title':
            title = node.text
            logger.debug("   Entry: " + title)

        elif parse_tag(node.tag) == 'content':
            description = node.text

        elif parse_tag(node.tag) == 'updated':
            updated = parse_timestamp(node.text, tz)

        elif parse_tag(node.tag) == 'recurrence':
            recurrence = node.text

        elif parse_tag(node.tag) == 'when':
            when = parse_timestamp(node.attrib["startTime"], tz)
            end_time = parse_timestamp(node.attrib["endTime"], tz)
            duration = time.mktime(end_time.timetuple()) - \
                time.mktime(when.timetuple())

            # Check for a "reminder" tag:
            for child_element in node.getchildren():
                if parse_tag(child_element.tag) == 'reminder':
                    reminder = int(child_element.get('minutes'))

        elif parse_tag(node.tag) == 'reminder':
            reminder = int(node.get('minutes'))

        elif parse_tag(node.tag) == 'where':
            where = node.text

        elif parse_tag(node.tag) == 'eventStatus':
            status = node.attrib["value"]
            if status == STATUS_CANCELLED:
                cancelled = True

        elif parse_tag(node.tag) == 'originalEvent':
            original_entry = node.attrib["href"]
            for child_element in node.getchildren():
                if parse_tag(child_element.tag) == 'when':
                    start_time = child_element.get('startTime')

            if not exceptions.has_key(original_entry):
                exceptions[original_entry] = []
            exceptions[original_entry].append(parse_timestamp(start_time, tz))

    if reminder is None:
        logger.debug("No reminder found for entry: %s" % title)

    # If the event being processed is a recurrence cancellation, skip the
    # actual event creation:
    if cancelled:
        return

    entry = None
    if recurrence != None:
        entry = RecurringEntry(entry_id, title, description, reminder,
            where, updated, recurrence, cal)
    else:
        entry = SingleOccurrenceEntry(entry_id, title, description, reminder,
            updated, when, int(duration), where, cal)
    cal.entries.append(entry)

