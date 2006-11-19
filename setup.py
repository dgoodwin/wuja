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

""" Wuja Distutils Setup Script """

__revision__ = "$Revision$"

from distutils.core import setup

setup(name="wuja",
    version='0.0.4',
    description='Gnome Google Calendar integration.',
    author='Devan Goodwin & James Bowes',
    author_email='dgoodwin@dangerouslyinc.com & jbowes@dangerouslyinc.com',
    url='http://dangerouslyinc.com',
    packages=['wuja'],
    package_dir={'wuja': 'src/wuja'},
    package_data={'wuja': ['data/*.xml', 'data/*.glade', 'data/*.png']},
    scripts=['bin/wuja'],
    # TODO: This sucks.
    data_files=[('../etc/gconf/schemas', ['data/wuja.schema'])]
)


################################################################################
#
#							GConf Installation
#
################################################################################
from commands import getstatusoutput
from os import putenv
# Get gconf's default source
cmd = "gconftool-2 --get-default-source"
err, out = getstatusoutput(cmd)

# Set up the gconf environment variable.
putenv('GCONF_CONFIG_SOURCE', out)

# Install gconf to the default source
cmd = "gconftool-2 --makefile-install-rule data/wuja.schema"
err, out = getstatusoutput(cmd)

if out:

	print "installing GConf schema files"

if err:

    print 'Error: installation of gconf schema files failed: %s' % out

# Kill the GConf daemon
cmd = "killall gconfd-2"
err, out = getstatusoutput(cmd)

if err:

	print "Problem shutting down gconf."

# Start the GConf daemon
cmd = "gconftool-2 --spawn"
err, out = getstatusoutput(cmd)

if err:

	print "Problem restarting down gconf."

print "wuja installation complete"
