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
import os
import os.path
import datetime

from logging import getLogger
from egg import trayicon
from datetime import timedelta
from dateutil.tz import tzlocal

from wuja.notifier import Notifier
from wuja.config import WujaConfiguration, ALERT_NOTIFICATION
from wuja.data import WUJA_DIR, GCONF_PATH
from wuja.calendar import CalendarWindow
from wuja.upgrade import UpgradeManager
from wuja.preferences import PreferencesDialog
from wuja.utils import find_file_on_path

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
        upgrade_manager = UpgradeManager()
        upgrade_manager.check()

        # TODO: Disabled and switched from use of AsyncNotifier on
        # 2007-02-05. Possible problem with pynotify and threading, threading
        # was our decision to disable to get users up and running with a 0.0.6
        # bugfix release. Re-enable once the issue is resolved.
        #gtk.gdk.threads_init()

        # Maintain a map of events that have alert windows open to ensure
        # we don't popup multiple windows for the same event that hasn't
        # been confirmed by the user:
        self.__open_alerts = {}

        self.config = WujaConfiguration(GCONF_PATH)
        self.notifier = None
        self.prefs_dialog = None
        self.calendar_window = None
        self.updating = False
        self.feed_update_event_source = None

        actions = (
            ("calendar", gtk.STOCK_INDEX, "View Calendar", None, None,
                self.__open_calendar),
            ("preferences", gtk.STOCK_PREFERENCES, None, None, None,
                self.__open_preferences_dialog),
            ("update_feeds", gtk.STOCK_REFRESH, "Update Feeds", None, None,
                self.__update_feeds),
            ("debug_feeds", gtk.STOCK_EXECUTE, "Debug Feeds", None, None,
                self.__debug_feeds),
            ("about", gtk.STOCK_ABOUT, None, None, None,
                self.__open_about_dialog),
            ("quit", gtk.STOCK_QUIT, None, None, None, self.destroy))
        action_group = gtk.ActionGroup("wuja_menu")
        action_group.add_actions(actions)

        ui_mgr = gtk.UIManager()
        ui_mgr.add_ui_from_file(find_file_on_path("wuja/data/wuja-menu.xml"))
        ui_mgr.insert_action_group(action_group, 0)

        self.menu = ui_mgr.get_widget("/wuja_menu")
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

        self.build_notifier()

    def _reset_feed_update(self):
        """ Restart the feed update timer. """
        self.feed_update_event_source = gobject.timeout_add(
            FEED_UPDATE_INTERVAL * 1000 * 60, self.notifier.update)
        logger.debug("Updating feeds from Google servers every %s minutes."
            % FEED_UPDATE_INTERVAL)

    def __update_feeds(self, widget):
        """
        Pass call to update feeds along to the notifier and reset
        timers.
        """
        gobject.source_remove(self.feed_update_event_source)
        self.notifier.update()
        self._reset_feed_update()

    def __debug_feeds(self, widget):
        """ Print out debug info on all feeds to the log file. """
        logger.info("Calendar Debug Info:")
        for cal in self.notifier.cache.load_all():
            logger.info(cal.title + ":")
            for entry in cal.entries:
                logger.info("   " + entry.get_debug_info())

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        # 1 = left, 2 = middle, 3 = right:
        self.menu.popup(None, None, None, data.button, data.time)

    def __open_preferences_dialog(self, widget):
        """ Open the preferences dialog. """
        self.prefs_dialog = PreferencesDialog(self.config, self.notifier)

    def __open_calendar(self, widget):
        """ Open the calendar display dialog. """
        self.calendar_window = CalendarWindow(self.notifier.cache, self.config)

    def __close_dialog(self, widget):
        """ Close the preferences dialog. """
        self.prefs_dialog.close()

    def __open_about_dialog(self, widget):
        """ Open the about dialog. """
        glade_file = 'wuja/data/wuja-about.glade'
        glade_xml = gtk.glade.XML(find_file_on_path(glade_file))
        about_dialog = glade_xml.get_widget('WujaAbout')

        signals = {
            'on_WujaAbout_close': self.__close_about_dialog,
        }
        glade_xml.signal_autoconnect(signals)

        about_dialog.show_all()

    def __close_about_dialog(self, widget, response):
        """ Close the about dialog. """
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

        self._reset_feed_update()

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
        if alert_type == ALERT_NOTIFICATION:
            alert_window = AlertNotification(event, self.tray_icon, self.config)
        else:
            alert_window = AlertDialog(event, self.config)

        alert_window.connect("alert-closed", self.on_alert_closed)
        self.__open_alerts[event.key] = alert_window

    def on_alert_closed(self, alert):
        self.__open_alerts.pop(alert.event.key)

    def main(self):
        """ Launches the GTK main loop. """
        gtk.main()



class AlertDisplay(gobject.GObject):

    def __init__(self, event, config):
        gobject.GObject.__init__(self)
        self.config = config

        logger.debug('Opening alert dialog for event: %s', event.entry.title)
        self.event = event

    def _accept_event(self):
        """ Called when the user accepts an alert. """
        self.event.accepted = True
        logger.debug("Accepted event: " + self.event.entry.title)
        self.emit('alert-closed')

    def _snooze_event(self):
        """
        Called when the user presses snooze. Destroys the alert
        window and sets appropriate status for the event in question.
        """

        logger.debug("Snoozing for " + str(self.config.get_snooze()) + 
            " minutes: " + self.event.entry.title)
        snooze_until = datetime.datetime.now(tzlocal()) + \
            datetime.timedelta(minutes=self.config.get_snooze())
        self.event.snooze_until = snooze_until

        # Warn if snoozing takes us beyond the start of the event:
        worst_case_notify_time = self.event.time - datetime.timedelta(minutes=1)
        if worst_case_notify_time <= self.event.snooze_until:
            warning = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, 
                buttons=gtk.BUTTONS_OK,
                message_format="Snooze for event \"" + self.event.entry.title +
                    "\" extends beyond or close to event start time. You " +
                    "may not receive another notification before this event " +
                    "begins.")
            warning.run()
            warning.destroy()

        self.emit('alert-closed')

gobject.signal_new("alert-closed", AlertDisplay, gobject.SIGNAL_ACTION,
    gobject.TYPE_BOOLEAN, ())



class AlertDialog(AlertDisplay):

    """ Window displayed when an alert is triggered. """

    def __init__(self, event, config):
        AlertDisplay.__init__(self, event, config)

        glade_file = 'wuja/data/alert-window.glade'
        window_name = 'window1'
        glade_alert = gtk.glade.XML(find_file_on_path(glade_file))
        alert_dialog = glade_alert.get_widget(window_name)

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
        when.set_text(event.time.strftime("%a %b %d %Y - " + 
            self.config.get_timestamp_format()))

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
        self._accept_event()
        widget.get_parent_window().destroy()

    def snooze_event(self, widget, event):
        """
        Called when the user presses snooze. Destroys the alert
        window and sets appropriate status for the event in question.
        """
        self._snooze_event()
        widget.get_parent_window().destroy()



class AlertNotification(AlertDisplay):

    def __init__(self, event, tray_icon, config):
        AlertDisplay.__init__(self, event, config)

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
            "Location - " + where
        if description != None:
            body += "\n" + description

        pynotify.init(title)
        notif = pynotify.Notification(title, body)
        notif.attach_to_widget(tray_icon)
        notif.set_timeout(0)
        notif.add_action('accept', 'Accept', self.accept_event)
        notif.add_action('snooze', 'Snooze', self.snooze_event)

        notif.show()

    def accept_event(self, notification, action):
        self._accept_event()

    def snooze_event(self, notification, action):
        self._snooze_event()



