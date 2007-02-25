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

""" Tests for the Wuja configuration object. """

__revision__ = "$Revision$"

import unittest
import gconf
import os.path

import settestpath
from wuja.config import WujaConfiguration
from wuja.config import DEFAULT_TIMESTAMP_FORMAT

GCONF_TEST_PATH = '/apps/wuja/test'

class WujaConfigurationTests(unittest.TestCase):

    def setUp(self):
        self.config = WujaConfiguration(GCONF_TEST_PATH)

    def tearDown(self):
        # NOTE: Couldn't find a way to actually delete the directory, this just
        # unsets all the properties beneath it.
        client = gconf.client_get_default()
        client.recursive_unset(GCONF_TEST_PATH,
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

    def test_ignore_empty_url(self):
        """ Add an emptry string URL and ensure it doesn't get added to
        the configuration.
        """
        self.assertEqual(0, len(self.config.get_feed_urls()))
        self.config.add_feed_url('')
        self.assertEqual(0, len(self.config.get_feed_urls()))

    def test_default_timestamp_format(self):
        """
        If no timestamp is defined in gconf, test that a default
        value is returned.
        """
        self.assertEqual(DEFAULT_TIMESTAMP_FORMAT,
            self.config.get_timestamp_format())

    def test_set_timestamp_format(self):
        client = gconf.client_get_default()
        self.assertEqual(None, client.get_string(os.path.join(GCONF_TEST_PATH,
            "timestamp_format")))
        new_format = "%H:%M"
        self.config.set_timestamp_format(new_format)
        self.assertEqual(new_format, self.config.get_timestamp_format())



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(WujaConfigurationTests))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="suite")

