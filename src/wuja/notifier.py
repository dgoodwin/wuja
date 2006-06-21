""" Components related to notifying listeners of events. """

__revision__ = "$Revision$"

import urllib2
import datetime

from logging import getLogger

from wuja.feedparser import FeedParser

# Grab feed URL's from a config file?
feedUrl = ("""http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jg""" +
    """dtbe815ps@group.calendar.google.com/private-f404480fd9b64f2f7""" +
    """cb78b2a3d6daf6a/full""")
logger = getLogger("notifier")

# Notify observers of events within this threshold. (defined in minutes)
DEFAULT_THRESHOLD = 15 # minutes

class Notifier:
    """ Update Google feeds and notify listeners when an alarm should
    be displayed.

    Notifiers do not manage any timers, callers are expected to
    indicate when to update the feeds and check for alarms that are
    due.
    """

    def __init__ (self, threshold=DEFAULT_THRESHOLD):
        self.observers = []
        self.events = []
        self.calendar_entries = []

        self.update()
        self.threshold = threshold

    def __notify_observers(self, event):
        """ Notify observers that an event is due. """
        for observer in self.observers:
            observer.notify(event)

    def update_events(self):
        """ Update events that are soon to occur.

        Note: does not refetch feeds from the Google servers. """
        self.events = []
        for entry in self.calendar_entries:
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(hours=1)
            events = entry.events(start_date, end_date)
            for entry in events:
                self.events.append(entry)

    def attach(self, observer):
        """ Register an observer. All observers will be notified
        when an alarm should be displayed.
        """
        self.observers.append(observer)

    def update(self):
        """ Update feeds from the Google servers. """
        logger.debug("Reading entries from calendar feed:")
        xml = urllib2.urlopen(feedUrl).read()
        parser = FeedParser(xml)
        self.calendar_entries = parser.entries()
        self.update_events()

    def check_for_notifications(self):
        """ Check for any pending notifications that need to be sent. """
        logger.debug("Checking for events:")
        for event in self.events:
            # Ignore previously accepted event alerts:
            if event.accepted:
                continue
            now = datetime.datetime.now()
            # Ignore events in the past:
            if event.when < now:
                continue

            # NOTE: Overriding the Google Calendar reminder option and always
            # notifying 15 minutes before an appointment:
            delta = event.when - now
            if delta < datetime.timedelta(minutes=self.threshold):
                logger.debug("Notifying observers: " + event.entry.title +
                    " @ " + str(event.when))
                self.__notify_observers(event)
        return True

