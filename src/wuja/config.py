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

""" Components related to Wuja's configuration. """

__revision__ = "$Revision$"

import gconf
import gobject
import os.path

from logging import getLogger
logger = getLogger("config")

from wuja.feed import FeedSource
from wuja.data import WUJA_DB_FILE
from wuja.model import Cache

ALERT_NOTIFICATION = 'notification'
ALERT_DIALOG = 'dialog'
DEFAULT_TIMESTAMP_FORMAT = "%I:%M%p"
DEFAULT_REMINDER = 10 # minutes
DEFAULT_SNOOZE = 10 # minutes
GCONF_FEED_URLS = "feed_urls"
GCONF_TIMESTAMP_FORMAT = "timestamp_format"
GCONF_DEFAULT_REMINDER = "default_reminder"
GCONF_SNOOZE = "snooze"

class WujaConfiguration(gobject.GObject):

    def __init__(self, gconf_path):
        gobject.GObject.__init__(self)

        self.__gconf_path = gconf_path

        self.client = gconf.client_get_default()
        self.urls_path = os.path.join(self.__gconf_path, GCONF_FEED_URLS)
        self.timestamp_format_path = os.path.join(self.__gconf_path,
            GCONF_TIMESTAMP_FORMAT)
        self.__reminder_path = os.path.join(self.__gconf_path, 
            GCONF_DEFAULT_REMINDER)
        self.__snooze_path = os.path.join(self.__gconf_path, 
            GCONF_SNOOZE)
        self.__db_file = WUJA_DB_FILE

    def get_feed_urls(self):
        """ Return the list of all currently configured feed URLs. """
        return self.client.get_list(self.urls_path, gconf.VALUE_STRING)

    def add_feed_url(self, url):
        """ Add a feed URL to the configuration.

        Ignore empty string URL's.
        """
        if url == '':
            return
        url = url.replace('/basic', '/full')

        current_urls = self.get_feed_urls()
        current_urls.append(url)
        self.__set_feed_urls(current_urls)

    def remove_feed_url(self, url):
        """ Remove a feed URL. """
        current_urls = self.get_feed_urls()
        current_urls.remove(url)
        self.__set_feed_urls(current_urls)

    def remove_all_feed_urls(self):
        """ Remove all feed URLs. """
        self.__set_feed_urls([])

    def get_feed_source(self):
        """
        Returns the appropriate FeedSource for this type of
        configuration.
        """
        return FeedSource()

    def get_cache(self):
        """
        Return a new cache class for this configuration.
        """
        return Cache(db=self.__db_file)

    def get_alert_type(self):
        # default to the dialog
        alert_type = ALERT_DIALOG
        # pynotify isn't available on all platforms yet, use it if we can.
        # in a few months we can ditch this.
        try:
            import pynotify
            alert_type = ALERT_NOTIFICATION
            logger.debug("Using pynotify for alert notification.")
        except ImportError, e:
            logger.debug("Pynotify not installed on system, using dialogs " +
                "for alert notification")
        return alert_type

    def __set_feed_urls(self, urls):
        self.client.set_list(self.urls_path, gconf.VALUE_STRING, urls)
        self.client.suggest_sync()
        self.emit("config-changed")

    def get_timestamp_format(self):
        """
        Returns the strftime format for timestamps as stored in gconf.
        If none is defined (i.e. after initial program install), returns
        a default constant defined in this module.
        """
        format = self.client.get_string(self.timestamp_format_path)
        if format is None:
            return DEFAULT_TIMESTAMP_FORMAT
        return format

    def set_timestamp_format(self, format):
        """ Set the timestamp format in gconf. """
        self.client.set_string(self.timestamp_format_path, format)
        self.client.suggest_sync()
        # Don't emit config changed, the timestamp format isn't important
        # enough to require an update.

    def get_reminder(self):
        """ Returns the default reminder time in minutes. """
        reminder_mins = self.client.get_int(self.__reminder_path)
        if reminder_mins is None or reminder_mins == 0:
            return DEFAULT_REMINDER
        return reminder_mins

    def set_reminder(self, reminder):
        """ Set the default reminder minutes in gconf. """
        self.client.set_int(self.__reminder_path, reminder)
        self.client.suggest_sync()
        # Don't emit config changed, the reminder isn't important
        # enough to require an update.

    def get_snooze(self):
        """ Returns the default snooze time in minutes. """
        snooze_mins = self.client.get_int(self.__snooze_path)
        if snooze_mins is None or snooze_mins == 0:
            return DEFAULT_SNOOZE
        return snooze_mins

    def set_snooze(self, snooze):
        """ Set the default snooze minutes in gconf. """
        self.client.set_int(self.__snooze_path, snooze)
        self.client.suggest_sync()



gobject.signal_new("config-changed", WujaConfiguration, gobject.SIGNAL_ACTION,
    gobject.TYPE_BOOLEAN, ())
