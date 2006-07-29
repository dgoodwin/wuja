""" Components related to notifying listeners of events. """

__revision__ = "$Revision$"

import urllib2
import datetime
import gtk

import gobject

from logging import getLogger

from wuja.model import Calendar

logger = getLogger("notifier")

class Notifier(gobject.GObject):
    """ Update Google feeds and notify listeners when an alarm should
    be displayed.

    Notifiers do not manage any timers, callers are expected to
    indicate when to update the feeds and check for alarms that are
    due.
    """

    def __init__ (self, config):
        gobject.GObject.__init__(self)
        self.config = config
        self.feed_source = config.get_feed_source()

        self.config.connect("config-changed", self.update_configuration)

        self.events = []
        self.calendar_entries = []

        # Maps URL's (which is all we store in gconf) to the friendly
        # feed name. (used by the preferences dialog) Will be populated
        # during calls to 'update'.
        self.url_title_dict = {}
        self.title_url_dict = {}

        self.update()

    def update(self):
        """ Update all feeds from Google's servers, check for upcoming
        events and create appropriate objects if necessary.
        """
        logger.debug("Updating feeds from Google servers.")
        start_time = datetime.datetime.now()
        feeds = self.config.get_feed_urls()

        # In the event of communication errors, don't wipe out our existing
        # calendar entries:
        temporary_entries = []
        try:
            for feed_url in feeds:
                results = list(Calendar.select(Calendar.q.url == feed_url))
                if len(results) == 0:
                    logger.debug("Found new feed!")
                    cal = self.feed_source.get_calendar(feed_url)
                    temporary_entries.extend(cal.entries)
                    self.url_title_dict[feed_url] = cal.title
                    self.title_url_dict[cal.title] = feed_url

                elif results[0].last_update != \
                    self.feed_source.get_feed_last_update(feed_url):
                    results[0].destroySelf()
                    logger.debug("Updating feed: " + results[0].title)
                    cal = self.feed_source.get_calendar(feed_url)
                    temporary_entries.extend(cal.entries)
                    self.url_title_dict[feed_url] = cal.title
                    self.title_url_dict[cal.title] = feed_url

                else:
                    logger.debug("Feed already up to date: %s (%s)" % \
                        (results[0].title, results[0].last_update))
                    temporary_entries.extend(results[0].entries)

        except urllib2.URLError:
            logger.error("Error reaching Google servers.")
            return True

        self.calendar_entries = temporary_entries
        logger.debug("Found %s calendar entries from %s feeds." %
            (str(len(self.calendar_entries)), str(len(feeds))))
        self.update_events()
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        logger.debug("Updated feeds in: %s" % delta)
        return True

    def update_configuration(self, config):
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
                    logger.debug("   " + str(event.time))
                    self.events.append(event)
                    if event.key in accepted_events:
                        logger.debug("Restoring accepted state for entry: " +
                            event.key)
                        event.accepted = True

    def check_for_notifications(self):
        """ Check for any pending notifications that need to be sent. """
        logger.debug("Checking for notifications.")
        for event in self.events:
            # Ignore previously accepted event alerts:
            if event.accepted:
                continue
            now = datetime.datetime.now()
            # Ignore events in the past:
            if event.time < now:
                continue
            if event.entry.reminder is None:
                continue

            delta = event.time - now
            if delta < datetime.timedelta(minutes=event.entry.reminder):
                logger.debug("Notifying observers for event: " +
                    event.entry.title)
                logger.debug("   When: " + str(event.time))
                logger.debug("   Reminder: " + str(event.entry.reminder) +
                    " minutes")
                self.emit("feeds-updated", event)
        return True

gobject.signal_new("feeds-updated", Notifier, gobject.SIGNAL_ACTION,
    gobject.TYPE_BOOLEAN, (gobject.TYPE_PYOBJECT,))
