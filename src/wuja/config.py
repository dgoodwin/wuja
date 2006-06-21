import gconf
import os.path

from logging import getLogger
logger = getLogger("notifier")

class WujaConfiguration:

    def __init__(self, gconfPath):
        self.__gconfPath = gconfPath

    def getFeedUrls(self):
        client = gconf.client_get_default()
        return client.get_list(os.path.join(self.__gconfPath, 'feed_urls'),
            gconf.VALUE_STRING)

    def addFeedUrl(self, url):
        client = gconf.client_get_default()
        client.add_dir(self.__gconfPath, gconf.CLIENT_PRELOAD_ONELEVEL)
        urlsPath = os.path.join(self.__gconfPath, 'feed_urls')
        currentUrls = client.get_list(urlsPath, gconf.VALUE_STRING)
        currentUrls.append(url)
        client.set_list(urlsPath, gconf.VALUE_STRING, currentUrls)

        # Seems to be required to get unit tests to pass, assuming sync is too
        # slow:
        client.suggest_sync()

