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

""" Module for handling upgrade actions. """

__revision__ = "$Revision$"

from logging import getLogger
logger = getLogger("upgrade")

import os
import os.path
import gconf

from wuja.data import GCONF_PATH, WUJA_DB_FILE, WUJA_DIR

GCONF_VERSION_KEY = "version"
WUJA_VERSION = "0.0.4" # Must be updated each time a release is published.

RELEASES = ["0.0.3", "0.0.4"]

class UpgradeManager:

    def __init__(self):
        self.gconf_client = gconf.client_get_default()
        # Build the list of all configured upgrade actions:
        self.__upgrade_actions = {}
        self.__upgrade_actions["0.0.4"] = [
            DeleteCacheAction(),
        ]

    def check(self):
        """
        Check if the currently installed version of wuja predates the
        version we're actually running, and perform all necessary upgrade
        actions if so.
        """
        logger.info("Checking if upgrade is required.")
        if self.is_fresh_install():
            logger.debug("Executing for the first time, no upgrade required.")
            return

        installed_version = self.get_installed_version()
        if installed_version == WUJA_VERSION:
            logger.info("Running version " + str(WUJA_VERSION) + ", no " +
                "upgrade required.")
            return

        logger.warn("Upgrade required.")
        logger.warn("   Installed: " + installed_version)
        logger.warn("   Current:   " + WUJA_VERSION)
        try:
            upgrade_path = RELEASES[RELEASES.index(installed_version) + 1:]
            logger.info("Upgrade path: " + str(upgrade_path))
        except ValueError:
            raise Exception("Unknown wuja version installed: " +
                installed_version)

        for ver in upgrade_path:
            if self.__upgrade_actions.has_key(ver):
                for action in self.__upgrade_actions[ver]:
                    action.perform()

        # Update the installed version if we've made it this far without error:
        self.set_installed_version()

    def get_installed_version(self):
        """
        Retrieve the currently installed version of wuja on this system.
        Currently this is stored as a Gconf property.
        """
        path = os.path.join(GCONF_PATH, GCONF_VERSION_KEY)
        logger.debug("Version Gconf path: " + path)
        installed_version = self.gconf_client.get_string(path)
        if installed_version is None:
            # Versioning was implemented for 0.0.4:
            installed_version = "0.0.3"
        logger.debug("Installed version: " + installed_version)
        return installed_version

    def set_installed_version(self):
        """
        Set the currently installed version to our latest. Meant to be called
        after a successful upgrade.
        """
        path = os.path.join(GCONF_PATH, GCONF_VERSION_KEY)
        logger.debug("Setting installed version to " + WUJA_VERSION)
        self.gconf_client.set_string(path, WUJA_VERSION)

    def is_fresh_install(self):
        """ Is this the first time wuja was run on this system? """
        if self.gconf_client.dir_exists(GCONF_PATH):
            return False
        return True

class DeleteCacheAction:

    """ Upgrade action to delete the existing Wuja cache. """

    def perform(self):
        cache_file = os.path.join(WUJA_DIR, WUJA_DB_FILE)
        logger.warn("Removing cache: " + cache_file)
        if os.path.exists(cache_file):
            os.remove(cache_file)

