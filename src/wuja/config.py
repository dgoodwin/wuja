import gconf
import os.path

from logging import getLogger
logger = getLogger("notifier")

class WujaConfiguration:

    def __init__(self, gconfPath):
        self.__gconfPath = gconfPath

    def get_feed_urls(self):
        client = gconf.client_get_default()
        return client.get_list(os.path.join(self.__gconfPath, 'feed_urls'),
            gconf.VALUE_STRING)

    def add_feed_url(self, url):
        client = gconf.client_get_default()
        client.add_dir(self.__gconfPath, gconf.CLIENT_PRELOAD_ONELEVEL)
        urls_path = os.path.join(self.__gconfPath, 'feed_urls')
        currentUrls = client.get_list(urls_path, gconf.VALUE_STRING)
        currentUrls.append(url)
        client.set_list(urls_path, gconf.VALUE_STRING, currentUrls)
        client.suggest_sync()

    def remove_feed_url(self, url):
        client = gconf.client_get_default()
        client.add_dir(self.__gconfPath, gconf.CLIENT_PRELOAD_ONELEVEL)
        urls_path = os.path.join(self.__gconfPath, 'feed_urls')
        currentUrls = client.get_list(urls_path, gconf.VALUE_STRING)
        currentUrls.remove(url)
        client.set_list(urls_path, gconf.VALUE_STRING, currentUrls)
        client.suggest_sync()

