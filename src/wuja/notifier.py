""" Components related to notifying listeners of events. """

__revision__ = "$Revision$"

import urllib2
import datetime

from logging import getLogger

from wuja.feedparser import FeedParser

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

    def __init__ (self, config, threshold=DEFAULT_THRESHOLD):
        self.config = config
        self.config.attach(self)
        self.observers = []
        self.events = []
        self.calendar_entries = []

        self.update()
        self.threshold = threshold

    def __notify_observers(self, event):
        """ Notify observers that an event is due. """
        for observer in self.observers:
            observer.notify(event)

    def attach(self, observer):
        """ Register an observer. All observers will be notified
        when an alarm should be displayed.
        """
        self.observers.append(observer)

    def update(self):
        """ Update all feeds from Google's servers and check for
        upcoming events.
        """
        logger.debug("Updating feeds from Google servers.")
        self.calendar_entries = []
        for feed_url in self.config.get_feed_urls():
            xml = urllib2.urlopen(feed_url).read()
            parser = FeedParser(xml)
            self.calendar_entries.extend(parser.entries())
        self.update_events()

    def update_configuration(self):
        """ Configuration has changed, update our feeds. """
        logger.debug("Configuration change.")
        self.update()

    def update_events(self):
        """ Check pre-fetched calendar entries for upcoming events.

        Note: Does not query Google's servers.
        """
        logger.debug("Updating events for calendar entries.")
        self.events = []

        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(hours=1)
        logger.debug("   start date: " + str(start_date))
        logger.debug("   end date: " + str(end_date))

        for entry in self.calendar_entries:
            events = entry.events(start_date, end_date)
            if len(events) > 0:
                logger.debug("Found events for: " + entry.title)
                for event in events:
                    logger.debug("   " + str(event.when))
                    self.events.append(event)

    def check_for_notifications(self):
        """ Check for any pending notifications that need to be sent. """
        logger.debug("Checking for notifications.")
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

