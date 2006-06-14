import time
import urllib2
import time
import datetime

from feedparser import FeedParser
from log import getLogger

# Grab feed URL's from a config file?
feedUrl = \
"""
http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps@group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full
"""
logger = getLogger("notifier")

# TODO: Switch to use Google's reminder settings once more reliable:
DEFAULT_THRESHOLD = 15 # minutes

class Notifier:

    def __init__ (self, threshold=DEFAULT_THRESHOLD):
        self.observers = []
        self.update()
        self.threshold = threshold

    def __notifyObservers(self, event):
        for o in self.observers:
            o.notify(event)

    def updateEvents(self):
        self.events = []
        for entry in self.calendarEntries:
            startDate = datetime.datetime.now()
            endDate = startDate + datetime.timedelta(hours=1)
            events = entry.events(startDate, endDate)
            for e in events:
                self.events.append(e)

    def attach(self, observer):
        """ Register an observer. """
        self.observers.append(observer)

    def update(self):
        """ Update feeds from the Google servers. """
        # TODO: Don't read the entire calendar every time
        logger.debug("Reading entries from calendar feed:")
        xml = urllib2.urlopen(feedUrl).read()
        parser = FeedParser(xml)
        self.calendarEntries = parser.entries()
        self.updateEvents()

    def checkForNotifications(self):
        """ Check for any pending notifications that need to be sent. """
        logger.debug("Checking for events:")
        for e in self.events:
            # Ignore previously accepted event alerts:
            if e.accepted:
                continue
            now = datetime.datetime.now()
            # Ignore events in the past:
            if e.when < now:
                continue

            # NOTE: Overriding the Google Calendar reminder option and always
            # notifying 15 minutes before an appointment:
            delta = e.when - now
            if delta < datetime.timedelta(minutes=self.threshold):
                logger.debug("Notifying observers: " + e.entry.title +
                    " @ " + str(e.when))
                self.__notifyObservers(e)
        return True

