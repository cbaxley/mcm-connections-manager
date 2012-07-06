# - coding: utf-8 -
#
# Copyright (C) 2009 Alejandro Ayuso
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
from mcm.common import constants

'''
Dialogs for MCM Connections Manager
'''

def show_question_dialog(title, message):
    """Display a Warning Dialog and return the response to the caller"""
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, title)
    dialog.format_secondary_text(message)
    response = dialog.run()
    dialog.destroy()
    return response

def show_error_dialog(title, message):
    """Display an error dialog to the user"""
    show_common_dialog(title, message, gtk.MESSAGE_ERROR)

def show_info_dialog(title, message):
    """Display an error dialog to the user"""
    show_common_dialog(title, message, gtk.MESSAGE_INFO)

def show_common_dialog(title, message, icon):
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, icon, gtk.BUTTONS_OK, title)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()

class FileSelectDialog(object):

    def __init__(self, is_export=False):
        self.response = gtk.RESPONSE_CANCEL
        self.error = None
        self.uri = None
        self.mime = None
        
        title = constants.select_file_to_import
        action = gtk.FILE_CHOOSER_ACTION_OPEN
        buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
        if is_export:
            title = constants.select_file_to_export
            action = gtk.FILE_CHOOSER_ACTION_SAVE
            buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK)
        
        self.dlg = gtk.FileChooserDialog(title, None, action, buttons)
        self.attach_filter(is_export)

    def attach_filter(self, is_export):
        _filter = gtk.FileFilter()
        _filter.set_name("MCM (Encrypted File)")
        _filter.add_pattern("*.mcm")
        self.dlg.add_filter(_filter)
        
        _filter = gtk.FileFilter()
        _filter.set_name("CSV (Comma-separated values)")
        _filter.add_mime_type("text/csv")
        _filter.add_pattern("*.csv")
        self.dlg.add_filter(_filter)
        
        if is_export:
            _filter = gtk.FileFilter()
            _filter.set_name("HTML (Web Page)")
            _filter.add_mime_type("text/html")
            _filter.add_pattern("*.html")
            _filter.add_pattern("*.htm")
            self.dlg.add_filter(_filter)

    def get_response(self):
        return self.response

    def get_filename(self):
        if self.uri.find(self.mime) == -1:
            self.uri += "." + self.mime
        return self.uri
    
    def get_mime(self):
        return self.dlg.get_filter()

    def run(self):
        self.response = self.dlg.run()
        self.uri = self.dlg.get_filename()
        filter_name = self.dlg.get_filter().get_name().lower()
        self.mime = filter_name.split(" ")[0]
        self.dlg.destroy()

class McmCheckbox(gtk.HBox):

    def __init__(self, title, pid=None, cluster=False, img=None):
        gtk.HBox.__init__(self, False)
        self.pid = pid
        
        if img:
            self._icon = gtk.Image()
            self._icon.set_from_stock(img, gtk.ICON_SIZE_MENU)
            self.pack_start(self._icon, True, True, 5)
        
        self._label = gtk.Label(title)
        self._current_alias = title
        self.pack_start(self._label, True, True, 0)
        
        if cluster:
            self._button = gtk.CheckButton()
            self._button.set_name("%s_button" % title)
            self._button.set_tooltip_text(constants.cluster_checkbox_tooltip)
            self.pack_start(self._button, False, False, 0)
            
        self.close_button = gtk.Button()
        self.close_button.set_relief(gtk.RELIEF_NONE)
        self.close_button.set_image(gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU))
        self.close_button.set_tooltip_text(constants.cluster_checkbox_tooltip)
        self.pack_start(self.close_button, False, False, 0)
        self.show_all()
        
        if cluster:
            self._button.hide()

    def get_active(self):
        if self._button:
            return self._button.get_active()
        return None
    
    def set_active(self, active=True):
        if self._button:
            self._button.set_active(active)
    
    def hide_checkbox(self):
        if self._button:
            self._button.hide()
        
    def show_checkbox(self):
        if self._button:
            self._button.show()

    def set_title(self, title):
        self._label.set_text(title)

    def get_title(self):
        return self._label.get_text()

    def get_current_alias(self):
        return self._current_alias

class DefaultColorSettings(object):
    def __init__(self):
        def_settings = gtk.settings_get_default()
        color_scheme = def_settings.get_property("gtk-color-scheme").strip()

        # In non-gnome WM this won't work
        if len(color_scheme) > 0:
            color_scheme = color_scheme.split("\n")

            settings = {}
            for prop in color_scheme:
                # property is of the type key: value
                prop = prop.split(": ")
                settings[prop[0]] = prop[1]
                
            self.tooltip_fg_color = gtk.gdk.color_parse(settings["tooltip_fg_color"])
            self.selected_bg_color = gtk.gdk.color_parse(settings["selected_bg_color"])
            self.tooltip_bg_color = gtk.gdk.color_parse(settings["tooltip_bg_color"])
            self.base_color = gtk.gdk.color_parse(settings["base_color"])
            self.fg_color = gtk.gdk.color_parse(settings["fg_color"])
            self.text_color = gtk.gdk.color_parse(settings["text_color"])
            self.selected_fg_color = gtk.gdk.color_parse(settings["selected_fg_color"])
            self.bg_color = gtk.gdk.color_parse(settings["bg_color"])
            
def get_terminals_menu(parent, ssh_alias=None):
        menu = gtk.Menu()
        copy = gtk.MenuItem(constants.copy)
        paste = gtk.MenuItem(constants.paste)
        search = gtk.MenuItem(constants.google_search)
        title = gtk.MenuItem(constants.set_title)
        menu.append(copy)
        menu.append(paste)
        menu.append(search)
        
        if ssh_alias:
            ipk = gtk.MenuItem(constants.install_key)
            ipk.alias = ssh_alias
            ipk.connect('activate', parent.install_public_key)
            menu.append(ipk)
        
        menu.append(gtk.SeparatorMenuItem())
        menu.append(title)
        
        copy.connect('activate', parent.do_copy)
        paste.connect('activate', parent.do_paste)
        search.connect('activate', parent.do_search)
        title.connect('activate', parent.set_title_tab_title)        
        
        menu.show_all()
        return menu