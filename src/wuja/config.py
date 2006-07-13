""" Components related to Wuja's configuration. """

__revision__ = "$Revision$"

import gconf
import gobject
import os.path

from wuja.feed import FeedSource

from logging import getLogger
logger = getLogger("notifier")


class WujaConfiguration(gobject.GObject):

    def __init__(self, gconf_path):
        gobject.GObject.__init__(self)

        self.__gconf_path = gconf_path

        self.client = gconf.client_get_default()
        self.urls_path = os.path.join(self.__gconf_path, "feed_urls")

    def get_feed_urls(self):
        """ Return the list of all currently configured feed URLs. """
        return self.client.get_list(self.urls_path, gconf.VALUE_STRING)

    def add_feed_url(self, url):
        """ Add a feed URL to the configuration.

        If the user specifies a URL ending with "/basic", switch it for
        "/full". (basic URL's do not contain enough information for
        Wuja to work, but basic is what Google Calendar links to by
        default on the settings page.
        """
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
        """ Returns the appropriate FeedSource for this type of
        configuration.
        """
        return FeedSource()

    def __set_feed_urls(self, urls):
        self.client.set_list(self.urls_path, gconf.VALUE_STRING, urls)
        self.client.suggest_sync()
        self.emit("config-changed")


gobject.signal_new("config-changed", WujaConfiguration, gobject.SIGNAL_ACTION,
    gobject.TYPE_BOOLEAN, ())
