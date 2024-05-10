#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# by Ricardo Lenz, 2016-jun
# riclc@hotmail.com
#

# NOTE: based on:
# 1) Bring back `BackSpace` Keyboard Shortcuts on nautilus and thunar - Ask Ubuntu
#    https://askubuntu.com/questions/289535/bring-back-backspace-keyboard-shortcuts-on-nautilus-and-thunar
# 2) riclc/nautilus_backspace: Brings back the Backspace shortcut to Nautilus
#    https://github.com/riclc/nautilus_backspace

import os, gi
gi.require_version('Nautilus', '3.0')
from gi.repository import GObject, Nautilus, Gtk, Gio, GLib

def ok():
    app = Gtk.Application.get_default()
    app.set_accels_for_action( "win.up", ["BackSpace"] )
    #print app.get_actions_for_accel("BackSpace")
    #print app.get_actions_for_accel("<alt>Up")


class BackspaceBack(GObject.GObject, Nautilus.LocationWidgetProvider):
    def __init__(self):
        pass

    def get_widget(self, uri, window):
        ok()
        return None

