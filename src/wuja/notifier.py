#   Wuja - Google Calendar (tm) notifications for the GNOME desktop.
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" Components related to notifying listeners of events. """

__revision__ = "$Revision$"

import datetime

import gobject

from logging import getLogger
from dateutil.tz import tzlocal
from wuja.feed import FeedOpenError
from wuja.decorators import threaded

logger = getLogger("notifier")

class Notifier(gobject.GObject):
    """ Update Google feeds and notify listeners when an alarm should
    be displayed.

    Notifiers do not manage any timers, callers are expected to
    indicate when to update the feeds and check for alarms that are
    due.
    """

    def __init__ (self, config, cache=None):
        gobject.GObject.__init__(self)
        self.config = config
        self.feed_source = config.get_feed_source()

        if cache is None:
            self.cache = config.get_cache()
        else:
            self.cache = cache

        self.config.connect("config-changed", self.update_configuration)

        self.events = []
        self.calendar_entries = []

        self.update()

    def update(self):
        """
        Update all feeds, maintain our local cache, and check for
        upcoming events.
        """
        logger.info("Updating feeds from Google servers.")
        start_time = datetime.datetime.now()
        feeds = self.config.get_feed_urls()

        # In the event of communication errors, don't wipe out our existing
        # calendar entries:
        temporary_entries = []
        try:
            for feed_url in feeds:
                if not self.cache.has_calendar(feed_url):
                    logger.debug("Found new feed!")
                    cal = self.feed_source.get_calendar(feed_url)
                    logger.debug("   Feed title: " + cal.title)
                    logger.debug("   Entries: " + str(len(cal.entries)))
                    self.cache.save(cal)
                    temporary_entries.extend(cal.entries)
                    continue

                cal = self.cache.load(feed_url)

                if cal.last_update != \
                    self.feed_source.get_feed_last_update(feed_url):

                    # Delete the old calendar:
                    title = cal.title
                    self.cache.delete(feed_url)

                    logger.debug("Updating feed: " + title)
                    cal = self.feed_source.get_calendar(feed_url)
                    self.cache.save(cal)
                    temporary_entries.extend(cal.entries)
                else:
                    logger.info("Feed already up to date: %s (%s)" % \
                        (cal.title, cal.last_update))
                    temporary_entries.extend(cal.entries)
        except FeedOpenError:
            logger.error("Error reaching Google servers.")
            return True

        # Remove calendar's no longer in our config:
        for cal in self.cache.load_all():
            try:
                feeds.index(cal.url)
            except ValueError:
                logger.debug("Removing calendar no longer in config: %s" %
                    cal.url)
                self.cache.delete(cal.url)

        self.cache.sync()

        self.calendar_entries = temporary_entries
        logger.info("Found %s calendar entries from %s feeds." %
            (str(len(self.calendar_entries)), str(len(feeds))))

        self.update_events()
        end_time = datetime.datetime.now()
        delta = end_time - start_time
        logger.info("Updated feeds in: %s" % delta)
        return True

    def update_configuration(self, config):
        """ Configuration has changed, update our feeds. """
        logger.info("Configuration change.")
        self.update()

    def update_events(self):
        """
        Check pre-fetched calendar entries for upcoming events.

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

        start_date = datetime.datetime.now(tzlocal())
        end_date = start_date + datetime.timedelta(hours=1)

        for entry in self.calendar_entries:
            events = entry.get_events_starting_between(start_date, end_date)
            if len(events) > 0:
                logger.debug("   " + entry.title)
                for event in events:
                    logger.debug("      " + str(event.time))
                    self.events.append(event)
                    if event.key in accepted_events:
                        logger.debug("Restoring accepted state for entry: " +
                            event.key)
                        event.accepted = True
        logger.debug("Found: " + str(len(self.events)) + " events")

    def check_for_notifications(self):
        """ Check for any pending notifications that need to be sent. """
        logger.debug("Checking for notifications.")
        for event in self.events:
            # Ignore previously accepted event alerts:
            if event.accepted:
                continue
            now = datetime.datetime.now(tzlocal())
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

class AsyncNotifier(Notifier):
    """ A Notifier that uses threads to be asyncronous. """

    @threaded
    def update(self):
        return Notifier.update(self)
