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

""" The main Wuja GTK application. """

__revision__ = "$Revision$"

import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade
import gobject
import sys
import os
import os.path

from logging import getLogger
from egg import trayicon
from datetime import timedelta

from wuja.notifier import Notifier
from wuja.config import WujaConfiguration
from wuja.data import WUJA_DIR, GCONF_PATH, WUJA_DB_FILE
from wuja.model import SingleOccurrenceEntry, RecurringEntry, Calendar

NOTIFICATION_INTERVAL = 1 # minutes between notification checks
FEED_UPDATE_INTERVAL = 10 # minutes between feed updates

logger = getLogger("wuja")

if not os.path.isdir(WUJA_DIR):
    logger.debug(WUJA_DIR + " not found, creating.")
    os.mkdir(WUJA_DIR)

class WujaApplication:

    """ The main Wuja application. """

    def __init__(self):
        logger.info("Starting application.")

        # Maintain a map of events that have alert windows open to ensure
        # we don't popup multiple windows for the same event that hasn't
        # been confirmed by the user:
        self.__open_alerts = {}

        self.config = WujaConfiguration(GCONF_PATH)
        self.notifier = None
        self.prefs_dialog = None
        self.feed_update_event_source = None
        self.build_notifier()

        actions = (("preferences", gtk.STOCK_PREFERENCES, None, None, None,
            self.__open_preferences_dialog),
            ("update_feeds", gtk.STOCK_REFRESH, "Update Feeds", None, None,
                self.__update_feeds),
            ("about", gtk.STOCK_ABOUT, None, None, None,
                self.__open_about_dialog),
            ("quit", gtk.STOCK_QUIT, None, None, None, self.destroy))
        action_group = gtk.ActionGroup("wuja_menu")
        action_group.add_actions(actions)

        ui = gtk.UIManager()
        ui.add_ui_from_file(find_file_on_path("wuja/data/wuja-menu.xml"))
        ui.insert_action_group(action_group, 0)

        self.menu = ui.get_widget("/wuja_menu")
        self.menu.show_all()

        self.tray_icon = trayicon.TrayIcon("wuja")
        self.tray_icon.connect('button_press_event', self.__clicked)

        tray_image = gtk.Image()
        tray_image.set_from_file(
            find_file_on_path("wuja/data/wuja-icon-24x24.png"))

        event_box = gtk.EventBox()
        event_box.add(tray_image)
        self.tray_icon.add(event_box)
        self.tray_icon.show_all()

    def __update_feeds(self, widget):
        """
        Pass call to update feeds along to the notifier and reset
        timers. """
        # Stop the feed update timer:
        gobject.source_remove(self.feed_update_event_source)

        self.notifier.update()

        # Restart the feed update timer from now:
        self.feed_update_event_source = gobject.timeout_add(
            FEED_UPDATE_INTERVAL * 1000 * 60, self.notifier.update)
        logger.debug("Updating feeds from Google servers every %s minutes."
            % FEED_UPDATE_INTERVAL)

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        # 1 = left, 2 = middle, 3 = right:
        self.menu.popup(None, None, None, data.button, data.time)

    def __open_preferences_dialog(self, widget):
        self.prefs_dialog = PreferencesDialog(self.config, self.notifier)

    def __close_dialog(self, widget):
        self.prefs_dialog.close()

    def __open_about_dialog(self, widget):
        glade_file = 'wuja/data/wuja-about.glade'
        glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        about_dialog = glade_xml.get_widget('WujaAbout')

        signals = {
            'on_WujaAbout_close': self.__close_about_dialog,
        }
        glade_xml.signal_autoconnect(signals)

        about_dialog.show_all()

    def __close_about_dialog(self, widget, response):
        widget.destroy()

    def build_notifier(self):
        """ Builds the notifier object. """
        self.notifier = Notifier(self.config)
        # register ourselves as an observer
        self.notifier.connect("feeds-updated", self.notify)

        gobject.timeout_add(NOTIFICATION_INTERVAL * 1000 * 60,
            self.notifier.check_for_notifications)
        self.notifier.check_for_notifications()
        logger.debug("Checking for notifications every %s minutes."
            % NOTIFICATION_INTERVAL)

        self.feed_update_event_source = gobject.timeout_add(
            FEED_UPDATE_INTERVAL * 1000 * 60, self.notifier.update)
        logger.debug("Updating feeds from Google servers every %s minutes."
            % FEED_UPDATE_INTERVAL)

    def delete_event(self, widget, event, data=None):
        """ GTK function. """
        return False

    def destroy(self, widget, data=None):
        """ Quit the application. """
        self.notifier.cache.close()
        gtk.main_quit()

    def notify(self, notifier, event):
        """
        Triggered by the notifier when a notifaction of an event needs to
        go out to the user.
        """
        self.display_notification(None, event)

    def display_notification(self, widget, event):
        """
        Display a notification for an event.

        Check first to see if we already have a notification open.
        """
        # Check if we already have a notification window open for this event:
        if self.__open_alerts.has_key(event.key):
            logger.debug("Alert window already open for event: " + \
                event.entry.title)
            return
        
        alert_type = self.config.get_alert_type()
        if alert_type == "dialog":
            alert_window = AlertDialog(event)
        elif alert_type == "notification":
            alert_window = AlertNotification(event, self.tray_icon)
        else:
            assert False

        alert_window.connect("alert-closed", self.on_alert_closed)
        self.__open_alerts[event.key] = alert_window

    def on_alert_closed(self, alert):
        self.__open_alerts.pop(alert.event.key)

    def main(self):
        """ Launches the GTK main loop. """
        gtk.main()


class AlertDisplay(gobject.GObject):
    pass

gobject.signal_new("alert-closed", AlertDisplay, gobject.SIGNAL_ACTION,
    gobject.TYPE_BOOLEAN, ())

class AlertDialog(AlertDisplay):

    """ Window displayed when an alert is triggered. """

    def __init__(self, event):
        gobject.GObject.__init__(self)
        logger.debug('Opening alert dialog for event: %s', event.entry.title)
        self.event = event

        glade_file = 'wuja/data/alert-window.glade'
        window_name = 'window1'
        glade_alert = gtk.glade.XML(find_file_on_path(glade_file))
        alert_dialog = glade_alert.get_widget('window1')

        signals = {
            'on_accept_button_clicked': self.accept_event,
        }
        glade_alert.signal_autoconnect(signals)

        title = glade_alert.get_widget('title')
        when = glade_alert.get_widget('when')
        duration = glade_alert.get_widget('duration')
        calendar = glade_alert.get_widget('calendar')
        where = glade_alert.get_widget('where')
        description = glade_alert.get_widget('description')

        title.set_text(event.entry.title)
        when.set_text(event.time.strftime("%a %b %d %Y - %I:%M%P"))

        calendar.set_text(event.entry.calendar.title)

        if event.entry.location is None:
            where.set_text("")
        else:
            where.set_text(str(event.entry.location))
        if event.entry.description is None:
            description.set_text("")
        else:
            description.set_text(event.entry.description)

        duration_delta = timedelta(seconds=event.entry.duration)
        duration.set_text(str(duration_delta))

        alert_dialog.show_all()

    def accept_event(self, widget):
        """ Called when the user accepts an alert. """
        self.event.accepted = True
        logger.debug("Accepted event: " + self.event.entry.title)
        widget.get_parent_window().destroy()
        self.emit('alert-closed')
    
    def snooze_event(self, widget, event):
        """
        Called when the user presses snooze. Destroys the alert
        window and sets appropriate status for the event in question.
        """
        logger.debug("Snoozed event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.emit('alert-closed')


class AlertNotification(AlertDisplay):

    def __init__(self, event, tray_icon):
        import pynotify
        pynotify.init('wuja')
        
        title = event.entry.title + " - Wuja"
        start_time = event.time.strftime("%a %b %d %Y - %I:%M%P")
        duration = str(timedelta(seconds=event.entry.duration))
        calendar = str(event.entry.calendar.title)
        where = str(event.entry.location)
        description = event.entry.description


        body = start_time + "\n" + \
            "Duration - " + duration + "\n"  + \
            "Calendar - " + calendar + "\n" + \
            "Location - " + where +  "\n" + \
            description

        pynotify.init(title)
        notif = pynotify.Notification(title, body)
        notif.attach_to_widget(tray_icon)
        notif.add_action('accept', 'Accept', self.accept_event)
        notif.add_action("snooze", 'Snooze', self.snooze_event)
        notif.show()

    def accept_event(self, notification, action):
        self.emit('alert-closed')

    def snooze_event(self, notification, action):
        self.emit('alert-closed')


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
        """

        add_url_textfield = self.glade_prefs.get_widget('entry1')

        url = add_url_textfield.get_text()
        url = url.replace('/basic', '/full')
        logger.info("Adding URL: " + url)
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

def find_file_on_path(pathname):
    """
    Scan the Python path and locate a file with the given name.

    See:
      http://www.linuxjournal.com/xstatic/articles/lj/0087/4702/4702l2.html
    """
    if os.path.isabs(pathname):
        return pathname
    for dirname in sys.path:
        candidate = os.path.join(dirname, pathname)
        if os.path.isfile(candidate):
            return candidate
    raise Exception("Could not find %s on the Python path."
        % pathname)

