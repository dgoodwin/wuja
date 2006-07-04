#!/usr/bin/env python

""" The main Wuja GTK application. """

__revision__ = "$Revision$"

import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade
import gobject
import sys

# Setup the Python path so it can find our uninstalled modules/packages:
sys.path.append('./src/')

from logging import getLogger
from egg import trayicon

from wuja.log import setup_logging

# Configure logging: (needs to be done before importing our modules)
confFileLocations = ["~/.wuja/logging.conf", "./logging.conf"]
setup_logging(confFileLocations)
logger = getLogger("wuja")

from wuja.notifier import Notifier
from wuja.config import WujaConfiguration

GCONF_PATH = "/apps/wuja/"
NOTIFICATION_INTERVAL = 1 # minutes between notification checks
FEED_UPDATE_INTERVAL = 10 # minutes between feed updates

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
            ("about", gtk.STOCK_ABOUT, None, None, None, None),
            ("quit", gtk.STOCK_QUIT, None, None, None, self.destroy))
        action_group = gtk.ActionGroup("wuja_menu")
        action_group.add_actions(actions)

        ui = gtk.UIManager()
        ui.add_ui_from_file("data/wuja-menu.xml")
        ui.insert_action_group(action_group, 0)

        self.menu = ui.get_widget("/wuja_menu")
        self.menu.show_all()

        #icon = gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO,
        #    gtk.ICON_SIZE_BUTTON)

        self.tray_icon = trayicon.TrayIcon("wuja")
        self.tray_icon.connect('button_press_event', self.__clicked)

        event_box = gtk.EventBox()
        event_box.add(gtk.Label("Wuja"))
        self.tray_icon.add(event_box)
        self.tray_icon.show_all()

    def __update_feeds(self, widget):
        """ Pass call to update feeds along to the notifier and reset
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
        self.prefs_dialog = PreferencesDialog(self.config)

    def __close_dialog(self, widget):
        self.prefs_dialog.close()

    def build_notifier(self):
        """ Builds the notifier object. """
        self.notifier = Notifier(self.config)
        self.notifier.attach(self) # register ourselves as an observer

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
        gtk.main_quit()

    def notify(self, event):
        """
        Triggered by the notifier when a notifaction of an event needs to
        go out to the user.
        """
        self.display_notification(None, event)

    def display_notification(self, widget, event):
        """ Display a notification for an event.

        Check first to see if we already have a notification open.
        """
        # Check if we already have a notification window open for this event:
        if self.__open_alerts.has_key(event.key):
            logger.debug("Alert window already open for event: " + \
                event.entry.title)
            return

        box = gtk.VBox()

        label = gtk.Label("Wake Up Jackass...")
        label.show()
        box.pack_start(label)

        label = gtk.Label(event.entry.title)
        label.show()
        box.pack_start(label)

        description = ""
        if event.entry.description != None:
            description = event.entry.description
        label = gtk.Label(description)
        label.show()
        box.pack_start(label)

        label = gtk.Label(event.when.strftime("%a %b %d %Y - %H:%M%P"))
        label.show()
        box.pack_start(label)

        button_box = gtk.HBox()
        button = gtk.Button("Accept")
        button.connect("clicked", self.accept_event, event)
        button.show()
        button_box.pack_start(button)

        button = gtk.Button("Snooze")
        button.connect("clicked", self.snooze_event, event)
        button.show()
        button_box.pack_start(button)

        button_box.show()
        box.pack_start(button_box)

        box.show()

        alert_window = gtk.Window()
        alert_window.set_title("Alert")
        alert_window.add(box)
        alert_window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        alert_window.show()
        alert_window.set_urgency_hint(True)

        self.__open_alerts[event.key] = alert_window

    def accept_event(self, widget, event):
        """ Called when the user accepts an alert. """
        event.accepted = True
        logger.debug("Accepted event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.__open_alerts.pop(event.key)

    def snooze_event(self, widget, event):
        """ Called when the user presses snooze. Destroys the alert
        window and sets appropriate status for the event in question.
        """
        logger.debug("Snoozed event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.__open_alerts.pop(event.key)

    def main(self):
        """ Launches the GTK main loop. """
        gtk.main()

class PreferencesDialog:
    """ Class to open, maintain, and close the Wuja preferences
    dialog.
    """

    def __init__(self, config):
        """ Open the preferences dialog. """
        logger.debug("Opening preferences dialog.")
        self.config = config
        glade_file = 'data/wuja-prefs.glade'
        window_name = 'dialog1'
        self.glade_prefs = gtk.glade.XML(glade_file)
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
        for url in self.config.get_feed_urls():
            logger.debug("Existing URL: " + url)
            it = urls_list.append()
            urls_list.set_value(iter, 0, self.notifier.url_title_dict[url])
        self.prefs_url_list.set_model(urls_list)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Feed URLs", renderer, text=0)
        self.prefs_url_list.append_column(column)

        self.prefs_dialog_widget.show_all()

    def __add_url(self, widget):
        """ Add a URL to the list. """
        add_url_textfield = self.glade_prefs.get_widget('entry1')

        url = add_url_textfield.get_text()
        logger.info("Adding URL: " + url)
        add_url_textfield.set_text('')

        self.config.add_feed_url(url)

        # Update the list:
        urls_list = self.glade_prefs.get_widget('treeview1').get_model()
        feed_title = self.notifier.url_title_dict[url]
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
        url_to_remove = self.notifier.title_url_dict[url_to_remove_title]
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

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

