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

    def get_feed_urls(self):
        client = gconf.client_get_default()
        return client.get_list(os.path.join(self.__gconf_path, 'feed_urls'),
            gconf.VALUE_STRING)

    def add_feed_url(self, url):
        client = gconf.client_get_default()
        urls_path = os.path.join(self.__gconf_path, 'feed_urls')
        current_urls = client.get_list(urls_path, gconf.VALUE_STRING)
        current_urls.append(url)
        client.set_list(urls_path, gconf.VALUE_STRING, current_urls)
        client.suggest_sync()

    def remove_feed_url(self, url):
        client = gconf.client_get_default()
        urls_path = os.path.join(self.__gconf_path, 'feed_urls')
        current_urls = client.get_list(urls_path, gconf.VALUE_STRING)
        current_urls.remove(url)
        client.set_list(urls_path, gconf.VALUE_STRING, current_urls)
        client.suggest_sync()

    def attach(self, observer):
        self.observers.append(observer)

    def notify_configuration_changed(self):
        for observer in self.observers:
            observer.update_configuration()
