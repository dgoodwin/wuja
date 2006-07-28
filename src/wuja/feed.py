""" Components for parsing the XML returned by Google's feeds. """

__revision__ = "$Revision$"

import time
import urllib2

from datetime import datetime
from elementtree import ElementTree
from logging import getLogger

from wuja.model import SingleOccurrenceEntry
from wuja.model import RecurringEntry

logger = getLogger("feed")

class FeedSource:
    """ Builds feeds objects given a URL and caches feed last updated
    times to prevent excessive network chatter.
    """
    def __init__(self):
        # Cache the feeds we've fetched thus far so we can compare their
        # updated times with the latest and avoid redownloading the whole
        # thing.
        self._cache = {}

    def get_feed(self, url):
        """ Return the feed object for the given URL. First checks the
        cache and latest updated time.
        """
        last_update = self._get_feed_last_update(url)
        if (self._cache.has_key(url) and self._cache[url].last_update ==
            last_update):
            feed = self._cache[url]
            return feed

        feed = Feed(self._get_feed_xml(url), last_update)
        logger.debug("Updating feed: " + feed.title)
        self._cache[url] = feed
        return feed

    def _get_feed_last_update(self, url):
        """ Fetch the last updated time for the given feed URL. """
        url_file = urllib2.urlopen(url)
        return url_file.headers['last-modified']

    def _get_feed_xml(self, url):
        """ Fetches the full XML source for the feed from Google's
        servers.
        """
        return urllib2.urlopen(url).read()

class Feed:
    """ Parses the XML provided and returns a list of calendar entries.
    """

    def __init__(self, xml, last_update):
        self.__root_node = ElementTree.XML(xml)
        self.entries = []
        self.title = None
        self.last_update = last_update
        for elem in self.__root_node.getchildren():
            if parse_tag(elem.tag) == "entry":
                self.entries.append(create_entry(elem, self.title))
            elif parse_tag(elem.tag) == "title":
                self.title = elem.text

def parse_tag(original_tag):
    """ Element Tree tags show up with a {url} prefix. """
    return original_tag.split("}")[1]

def parse_timestamp(timestamp):
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
        int(second))

def create_entry(elem, feed_title):
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
    for node in elem.getchildren():
        if parse_tag(node.tag) == 'id':
            entry_id = node.text
        elif parse_tag(node.tag) == 'title':
            title = node.text
        elif parse_tag(node.tag) == 'content':
            description = node.text
        elif parse_tag(node.tag) == 'updated':
            updated = parse_timestamp(node.text)
        elif parse_tag(node.tag) == 'recurrence':
            recurrence = node.text
        elif parse_tag(node.tag) == 'when':
            when = parse_timestamp(node.attrib["startTime"])
            end_time = parse_timestamp(node.attrib["endTime"])
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

    if reminder is None:
        logger.debug("No reminder found for entry: %s" % title)

    if recurrence != None:
        return RecurringEntry(entry_id=entry_id, title=title,
            description=description, reminder=reminder, location=where,
            updated=updated, recurrence=recurrence, feed_title=feed_title)
    return SingleOccurrenceEntry(entry_id=entry_id, title=title,
        description=description, reminder=reminder, updated=updated,
        time=when, duration=int(duration), location=where,
        feed_title=feed_title)

