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

import gtk
import gobject

from logging import getLogger

logger = getLogger("wuja")

from wuja.calendar import find_file_on_path

class PreferencesDialog:

    """
    Class to open, maintain, and close the Wuja preferences
    dialog.
    """

    def __init__(self, config, notifier):
        """ Open the preferences dialog. """
        logger.debug("Opening preferences dialog.")
        self.config = config
        self.notifier = notifier

        glade_file = 'wuja/data/wuja-prefs.glade'
        window_name = 'dialog1'
        self.glade_prefs = gtk.glade.XML(find_file_on_path(glade_file))
        signals = {
            'on_add_clicked' : self.__add_url,
            'on_remove_clicked' : self.__remove_url,
            'on_remove_all_clicked' : self.__remove_all_urls,
            'on_help_clicked' : self.__display_help,
            'on_close_clicked' : self.close
        }
        self.glade_prefs.signal_autoconnect(signals)
        self.prefs_dialog_widget = self.glade_prefs.get_widget(window_name)

        # Populate the list of existing URLs:
        self.prefs_url_list = self.glade_prefs.get_widget('treeview1')
        urls_list = gtk.ListStore(gobject.TYPE_STRING)
        self.__title_index = {}
        for url in self.config.get_feed_urls():
            logger.debug("Existing URL: " + url)
            it = urls_list.append()
            cal = self.notifier.cache.load(url)
            urls_list.set_value(it, 0, cal.title)
            self.__title_index[cal.title] = cal
        self.prefs_url_list.set_model(urls_list)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Feed URLs", renderer, text=0)
        self.prefs_url_list.append_column(column)

        self.prefs_dialog_widget.show_all()

    def __add_url(self, widget):
        """ Add a URL to the list.

        If the user specifies a URL ending with "/basic", switch it for
        "/full". (basic URL's do not contain enough information for
        Wuja to work, but basic is what Google Calendar links to by
        default on the settings page.

        If the URL is not valid or unreachable, display an error dialog
        and skip adding the URL.
        """

        add_url_textfield = self.glade_prefs.get_widget('entry1')

        url = add_url_textfield.get_text()
        url = process_url(url)

        # Check if the URL is valid before we try to add it:
        logger.info("Verifying URL: " + url)
        try:
            url_file = urllib2.urlopen(url)
        except Exception:
            logger.error("URL not valid!")
            error_dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                message_format="Invalid URL", buttons=gtk.BUTTONS_OK)
            error_dialog.run()
            error_dialog.destroy()
            return

        add_url_textfield.set_text('')

        self.config.add_feed_url(url)

        # Update the list:
        urls_list = self.glade_prefs.get_widget('treeview1').get_model()
        cal = self.notifier.cache.load(url)
        feed_title = cal.title
        urls_list.set_value(urls_list.append(), 0, feed_title)

    def __remove_url(self, widget):
        """ Remove a URL from the list. """
        urls_list = self.glade_prefs.get_widget('treeview1')
        selection = urls_list.get_selection()
        (model, it) = selection.get_selected()
        if it is None:
            logger.debug("Unable to remove URL, no entry selected.")
            return
        url_to_remove_title = model.get_value(it, 0)
        cal = self.__title_index[url_to_remove_title]
        url_to_remove = cal.url
        logger.info("Removing URL for feed %s: %s" % (url_to_remove_title,
            url_to_remove))
        model.remove(it)
        self.config.remove_feed_url(url_to_remove)

    def __remove_all_urls(self, widget):
        """ Remove all URL's from the list. """
        logger.warn("Removing *ALL* URLs.")
        self.config.remove_all_feed_urls()

        urls_list = self.glade_prefs.get_widget('treeview1')
        urls_list.set_model()

    def __display_help(self, widget):
        """ Display preferences help. """
        logger.info("Help clicked")

    def close(self, widget):
        """ Close the preferences dialog. """
        self.prefs_dialog_widget.destroy()
        self.prefs_dialog = None




