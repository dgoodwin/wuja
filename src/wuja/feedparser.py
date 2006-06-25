""" Components for parsing the XML returned by Google's feeds. """

__revision__ = "$Revision$"

import time

from datetime import datetime
from elementtree import ElementTree
from model import SingleOccurrenceEntry
from model import RecurringEntry
from logging import getLogger

logger = getLogger("feedparser")

class FeedParser:
    """ Parses the XML provided and returns a list of calendar entries. """

    def __init__(self, xml):
        self.root_node = ElementTree.XML(xml)

    def entries(self):
        events = []
        for elem in self.root_node.getchildren():
            if parse_tag(elem.tag) == "entry":
                events.append(create_entry(elem))
        return events

def parse_tag(originalTag):
    """ Element Tree tags show up with a {url} prefix. """
    return originalTag.split("}")[1]

def parse_timestamp(timestamp):
    """ Convert internet timestamp (RFC 3339) into a Python datetime object. """
    # NOTE: Couldn't find anything in the standard python library to parse
    # these for us:
    date, time = timestamp.split('T')
    time, timezone = time.split('.')
    # NOTE: Not using timezone right now, dates here seem to always come
    # back GMT.
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(int(year), int(month), int(day), int(hour), int(minute),
        int(second))

def create_entry(elem):
    """ Parses calender entry XML into an Entry object. """
    id = None
    title = None
    description = None
    updated = None
    recurrence = None
    when = None
    where = None
    duration = None
    for node in elem.getchildren():
        if parse_tag(node.tag) == 'id':
            id = node.text
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
            endTime = parse_timestamp(node.attrib["endTime"])
            duration = time.mktime(endTime.timetuple()) - \
                time.mktime(when.timetuple())
        elif parse_tag(node.tag) == 'where':
            where = node.text
    logger.debug("Found entry: " + title)
    if recurrence != None:
        return RecurringEntry(id, title, description, where, updated,
            recurrence)
    return SingleOccurrenceEntry(id, title, description, updated, when,
        duration, "where")

