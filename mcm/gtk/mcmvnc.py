# - coding: utf-8 -
#
# Copyright (C) 2010 Alejandro Ayuso
#
# This file is part of the MCM Connection Manager
#
# MCM Connection Manager is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# MCM Connection Manager is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the MCM Connection Manager. If not, see
# <http://www.gnu.org/licenses/>.
#


import gtk
import gtkvnc
from time import strftime

from mcm.common.constants import *
from widgets import UtilityDialogs

class McmVncClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.vnc = self.new_vnc_client()
        self.menu = self.new_vnc_menu()
        self.layout = gtk.VBox()
        self.layout.pack_start(self.menu, False, True, 0)
        self.layout.pack_start(self.vnc, True, True, 0)

    def new_vnc_client(self):
        # We add any configuration here
        v = gtkvnc.Display()
        v.set_pointer_grab(True)
        v.set_keyboard_grab(True)
        v.connect("vnc-connected", self.vnc_connected)
        v.connect("vnc-disconnected", self.vnc_connected)
        return v

    def new_vnc_menu(self):
        menubar = gtk.MenuBar()

        sendkeys = gtk.MenuItem(tools)
        menubar.append(sendkeys)

        scrs = gtk.MenuItem(screenshot)
        caf1 = gtk.MenuItem("Ctrl+Alt+F_1")
        caf7 = gtk.MenuItem("Ctrl+Alt+F_7")
        cad = gtk.MenuItem("Ctrl+Alt+_Del")
        cab = gtk.MenuItem("Ctrl+Alt+_Backspace")
        disc = gtk.MenuItem(disconnect)
        sep = gtk.SeparatorMenuItem()

        submenu = gtk.Menu()
        submenu.append(caf1)
        submenu.append(caf7)
        submenu.append(cad)
        submenu.append(cab)
        submenu.append(sep)
        submenu.append(scrs)
        submenu.append(disc)
        sendkeys.set_submenu(submenu)

        caf1.connect("activate", self.send_caf1)
        caf7.connect("activate", self.send_caf7)
        cad.connect("activate", self.send_cad)
        cab.connect("activate", self.send_cab)
        scrs.connect("activate", self.screenshot_event)
        disc.connect("activate", self.disconnect_event)
        return menubar

    def get_instance(self):
        self.vnc.open_host(self.host, self.port)
        #self.vnc.realize()
        return self.layout

    def vnc_connected(self, widget):
        print "Connected to server"

    def send_caf1(self, menuitem):
        self.vnc.send_keys(["Control_L", "Alt_L", "F1"])

    def send_caf7(self, menuitem):
        self.vnc.send_keys(["Control_L", "Alt_L", "F7"])

    def send_cad(self, menuitem):
        self.vnc.send_keys(["Control_L", "Alt_L", "Del"])

    def send_cab(self, menuitem):
        self.vnc.send_keys(["Control_L", "Alt_L", "BackSpace"])

    def screenshot_event(self, menuitem):
        filename = "/tmp/mcm_vnc_screenshot_%s.png" % strftime("%Y%m%d.%H%M%S")
        dlg = UtilityDialogs()
        dlg.show_info_dialog(screenshot_info, filename)
        pix = self.vnc.get_pixbuf()
        pix.save(filename, "png", { "tEXt::Generator App": "MCM Connections Manager" })

    def disconnect_event(self, menuitem):
        self.vnc.close()
