import time

from datetime import datetime
from elementtree import ElementTree
from model import SingleOccurrenceEntry
from model import RecurringEntry

class FeedParser:

    def __init__(self, xml):
        self.rootNode = ElementTree.XML(xml)

    def entries(self):
        events = []
        for elem in self.rootNode.getchildren():
            # TODO: Is there a better way to examine tag names?
            if parseTag(elem.tag) == "entry":
                events.append(createEntry(elem))
        return events

def parseTag(originalTag):
    """ Element Tree tags show up with a {url} prefix. """
    return originalTag.split("}")[1]

def parseTimestamp(timestamp):
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

def createEntry(elem):
    """ Parses calender entry XML into an Entry object. """
    id = None
    title = None
    description = None
    updated = None
    recurrence = None
    when = None
    duration = None
    for node in elem.getchildren():
        if parseTag(node.tag) == 'id':
            id = node.text
        elif parseTag(node.tag) == 'title':
            title = node.text
        elif parseTag(node.tag) == 'content':
            description = node.text
        elif parseTag(node.tag) == 'updated':
            updated = parseTimestamp(node.text)
        elif parseTag(node.tag) == 'recurrence':
            recurrence = parseRecurrence(node.text)
        elif parseTag(node.tag) == 'when':
            when = parseTimestamp(node.attrib["startTime"])
            endTime = parseTimestamp(node.attrib["endTime"])
            duration = time.mktime(endTime.timetuple()) - \
                time.mktime(when.timetuple())
    if recurrence != None:
        return RecurringEntry(id, title, description, updated, recurrence)
    return SingleOccurrenceEntry(id, title, description, updated, when,
        duration, "where")

def parseRecurrence(recurrence):
    """ Parses the recurrence field. (iCalendar format, see RFC 2445) """
    import vobject
    parsed = vobject.readOne(recurrence)
    #parsed.prettyPrint()
    return recurrence # TODO: Change this...
