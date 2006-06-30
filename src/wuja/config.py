""" Components related to Wuja's configuration. """

__revision__ = "$Revision$"

import gconf
import os.path

from logging import getLogger
logger = getLogger("notifier")

class WujaConfiguration:

    def __init__(self, gconf_path):
        self.__gconf_path = gconf_path
        self.observers = []

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

    def attach(self, observer):
        """ Register an observer. Observer must have an
        "update_configuration" method.
        """
        self.observers.append(observer)

    def notify_configuration_changed(self):
        """ Notify observers that the configuration has been changed.
        """
        for observer in self.observers:
            observer.update_configuration()

    def __set_feed_urls(self, urls):
        self.client.set_list(self.urls_path, gconf.VALUE_STRING, urls)
        self.client.suggest_sync()
        self.notify_configuration_changed()

