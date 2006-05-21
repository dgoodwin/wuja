from elementtree import ElementTree
from model import Event

class FeedParser:
    def __init__(self, xml):
        self.rootNode = ElementTree.XML(xml)

    def events(self):
        events = []
        for elem in self.rootNode.getchildren():
            # TODO: Is there a better way to examine tag names?
            if parseTag(elem.tag) == "entry":
                events.append(createEvent(elem))
        return events

def parseTag(originalTag):
    """ Element Tree tags show up with a {url} prefix. """
    return originalTag.split("}")[1]

def createEvent(elem):
    """ Parses calender entry XML into an Event object. """
    id = None
    for node in elem.getchildren():
        #print node.tag
        if parseTag(node.tag) == 'id':
            id = node.text
    return Event(id)

