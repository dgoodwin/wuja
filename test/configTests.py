import unittest
import gconf

import settestpath
from wuja.config import WujaConfiguration

gconfTestPath = '/apps/wuja/test'

class WujaConfigurationTests(unittest.TestCase):

    def setUp(self):
        self.config = WujaConfiguration(gconfTestPath)

    def testAddFeedUrl(self):
        self.config.addFeedUrl('url1')
        urls = self.config.getFeedUrls()
        self.assertEqual(1, len(urls))
        self.assertEqual('url1', urls[0])

    def testAddMultipleFeedUrls(self):
        self.config.addFeedUrl('url1')
        self.config.addFeedUrl('url2')
        self.config.addFeedUrl('url3')
        urls = self.config.getFeedUrls()
        self.assertEqual(3, len(urls))

    def tearDown(self):
        # NOTE: Couldn't find a way to actually delete the directory, this just
        # unsets all the properties beneath it.
        client = gconf.client_get_default()
        client.recursive_unset(gconfTestPath, gconf.UNSET_INCLUDING_SCHEMA_NAMES)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(WujaConfigurationTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

