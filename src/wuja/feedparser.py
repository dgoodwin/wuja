""" Components for parsing the XML returned by Google's feeds. """

__revision__ = "$Revision$"

import time

from datetime import datetime
from elementtree import ElementTree
from logging import getLogger

from wuja.model import SingleOccurrenceEntry
from wuja.model import RecurringEntry

logger = getLogger("feedparser")

class FeedParser:
    """ Parses the XML provided and returns a list of calendar entries.
    """

    def __init__(self, xml):
        self.__root_node = ElementTree.XML(xml)
        self.entries = []
        self.title = None
        for elem in self.__root_node.getchildren():
            if parse_tag(elem.tag) == "entry":
                self.entries.append(create_entry(elem))
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

def create_entry(elem):
    """ Parses calender entry XML into an Entry object. """
    entry_id = None
    title = None
    description = None
    updated = None
    recurrence = None
    when = None
    where = None
    duration = None
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
        elif parse_tag(node.tag) == 'where':
            where = node.text
    if recurrence != None:
        return RecurringEntry(entry_id, title, description, where, updated,
            recurrence)
    return SingleOccurrenceEntry(entry_id, title, description, updated, when,
        duration, where)

