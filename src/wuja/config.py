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

from wuja.feed import FeedSource
from wuja.data import WUJA_DB_FILE
from wuja.model import Cache

class WujaConfiguration(gobject.GObject):

    def __init__(self, gconf_path):
        gobject.GObject.__init__(self)

        self.__gconf_path = gconf_path

        self.client = gconf.client_get_default()
        self.urls_path = self.__gconf_path + "feed_urls"
        self.alert_path = self.__gconf_path + "feed_urls"
        self.__db_file = WUJA_DB_FILE

    def get_feed_urls(self):
        """ Return the list of all currently configured feed URLs. """
        return self.client.get_list(self.urls_path, gconf.VALUE_STRING)

    def add_feed_url(self, url):
        """ Add a feed URL to the configuration.

        If the user specifies a URL ending with "/basic", switch it for
        "/full". (basic URL's do not contain enough information for
        Wuja to work, but basic is what Google Calendar links to by
        default on the settings page.

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
        return self.client.get_string(self.alert_path)

    def __set_feed_urls(self, urls):
        self.client.set_list(self.urls_path, gconf.VALUE_STRING, urls)
        self.client.suggest_sync()
        self.emit("config-changed")

gobject.signal_new("config-changed", WujaConfiguration, gobject.SIGNAL_ACTION,
    gobject.TYPE_BOOLEAN, ())
