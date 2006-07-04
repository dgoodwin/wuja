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
        self.threshold = threshold

        self.config.attach(self)
        self.observers = []
        self.events = []
        self.calendar_entries = []

        # Maps URL's (which is all we store in gconf) to the friendly
        # feed name. (used by the preferences dialog) Will be populated
        # during calls to 'update'.
        self.url_title_dict = {}
        self.title_url_dict = {}

        self.update()

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
        feeds = self.config.get_feed_urls()

        # In the event of communication errors, don't wipe out our existing
        # calendar entries:
        temporary_entries = []

        try:
            for feed_url in feeds:
                xml = urllib2.urlopen(feed_url).read()
                parser = FeedParser(xml)
                temporary_entries.extend(parser.entries)
                self.url_title_dict[feed_url] = parser.title
                self.title_url_dict[parser.title] = feed_url
                logger.debug("Processed feed: " + parser.title)
        except urllib2.URLError:
            logger.warn("Error updating feeds.")
        self.calendar_entries = temporary_entries
        logger.debug("Found %s calendar entries from %s feeds." %
            (str(len(self.calendar_entries)), str(len(feeds))))
        self.update_events()
        return True

    def update_configuration(self):
        """ Configuration has changed, update our feeds. """
        logger.debug("Configuration change.")
        self.update()

    def update_events(self):
        """ Check pre-fetched calendar entries for upcoming events.

        Note: Does not query Google's servers.
        """
        logger.debug("Updating events for calendar entries.")

        # Maintain confirmed status on events:
        accepted_events = set()
        for event in self.events:
            if event.accepted:
                logger.debug("Saving accepted state for entry: " + event.key)
                accepted_events.add(event.key)

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
                    if event.key in accepted_events:
                        logger.debug("Restoring accepted state for entry: " +
                            event.key)
                        event.accepted = True

    def check_for_notifications(self):
        """ Check for any pending notifications that need to be sent. """
        logger.debug("Checking for notifications within next " +
            str(self.threshold) + " minutes.")
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

