import unittest
import gconf

import settestpath
from wuja.config import WujaConfiguration

gconfTestPath = '/apps/wuja/test'

class WujaConfigurationTests(unittest.TestCase):

    def setUp(self):
        self.config = WujaConfiguration(gconfTestPath)

    def tearDown(self):
        # NOTE: Couldn't find a way to actually delete the directory, this just
        # unsets all the properties beneath it.
        client = gconf.client_get_default()
        client.recursive_unset(gconfTestPath,
            gconf.UNSET_INCLUDING_SCHEMA_NAMES)

    def test_add_feed_url(self):
        self.config.add_feed_url('url1')
        urls = self.config.get_feed_urls()
        self.assertEqual(1, len(urls))
        self.assertEqual('url1', urls[0])

    def test_add_multiple_feed_urls(self):
        urls = ['url1', 'url2', 'url3']
        for url in urls:
            self.config.add_feed_url(url)
        result_urls = self.config.get_feed_urls()
        self.assertEqual(urls, result_urls)

    def test_remove_feed_url(self):
        urls = ['url1', 'url2', 'url3']
        for url in urls:
            self.config.add_feed_url(url)
        self.config.remove_feed_url(urls[1])
        self.assertEqual([urls[0], urls[2]], self.config.get_feed_urls())

    def test_remove_nonexistent_url(self):
        urls = ['url1', 'url2', 'url3']
        for url in urls:
            self.config.add_feed_url(url)
        self.assertRaises(ValueError, self.config.remove_feed_url,
            'not a real url')

    def test_remove_all_urls(self):
        urls = ['url1', 'url2', 'url3']
        for url in urls:
            self.config.add_feed_url(url)
        self.config.remove_all_feed_urls()
        self.assertEqual(0, len(self.config.get_feed_urls()))

    def test_basic_url_replacement(self):
        """ /basic URLs lack data Wuja needs. """
        urls = ['url1/basic']
        for url in urls:
            self.config.add_feed_url(url)
        lookup_urls = self.config.get_feed_urls()
        self.assertEqual('url1/full', lookup_urls[0])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(WujaConfigurationTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

