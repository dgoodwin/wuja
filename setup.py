""" Wuja Distutils Setup Script """

__revision__ = "$Revision$"

from distutils.core import setup

setup(name="Wuja",
    version='0.1',
    description='Gnome Google Calendar integration.',
    author='Devan Goodwin & James Bowes',
    author_email='dgoodwin@dangerouslyinc.com & jbowes@dangerouslyinc.com',
    url='http://dangerouslyinc.com',
    packages=['wuja'],
    package_dir={'wuja': 'src/wuja'},
    scripts=['bin/wuja'],
    data_files=[('data', ['data/wuja-menu.xml', 'data/wuja-prefs.glade'])],
)
