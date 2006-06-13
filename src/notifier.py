import time
import urllib2
import time
import datetime

from feedparser import FeedParser

# Grab feed URL's from a config file?
feedUrl = \
"""
http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps@group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full
"""

class Notifier:

    def __init__ (self, threshold=1):
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
        print("Reading entries from calendar feed:")
        xml = urllib2.urlopen(feedUrl).read()
        parser = FeedParser(xml)
        self.calendarEntries = parser.entries()
        self.updateEvents()

    def checkForNotifications(self):
        """ Check for any pending notifications that need to be sent. """
        # TODO: Need to be careful here, especially the way things are now.
        # (checking for events within the next 60 seconds, every 60 seconds)
        # Change to look for any UNCONFIRMED events within 5 or 10 minutes in
        # either direction.
        for e in self.events:
            now = datetime.datetime.now()
            delta = e.when - now
            if delta < datetime.timedelta(minutes=self.threshold):
                self.__notifyObservers(e)
        return True

