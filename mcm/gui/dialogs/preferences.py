# - coding: utf-8 -
#
# Copyright (C) 2009 Alejandro Ayuso 
#
# This file is part of the MCM Connection Manager
#
# MCM Connection Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MCM Connection Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the MCM Connection Manager.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import gtk

from mcm.common import constants
from mcm.gui.widgets import DefaultColorSettings

class PreferencesDialog(object):

    def __init__(self, conf):
        self.conf = conf
        self.response = gtk.RESPONSE_CANCEL
        self.default_color = DefaultColorSettings().base_color
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_preferences)
        self.dlg = self.builder.get_object('dialog_preferences')
        self.widgets = {
            # Consoles
            'fontbutton': self.builder.get_object('fontbutton'),
            'color_scheme_combo': self.builder.get_object('color_scheme_combo'),
            'buffer_hscale': self.builder.get_object('buffer-hscale'),
            'console_char_entry': self.builder.get_object('console_char_entry'),
            # Connections
            'ssh_options_entry': self.builder.get_object('ssh_default_options_entry'),
            'vnc_options_entry': self.builder.get_object('vnc_default_options_entry'),
            'rdp_options_entry': self.builder.get_object('rdp_default_options_entry'),
            'telnet_options_entry': self.builder.get_object('telnet_default_options_entry'),
            'ftp_options_entry': self.builder.get_object('ftp_default_options_entry'),
            'ssh_entry': self.builder.get_object('ssh_client_entry'),
            'vnc_entry': self.builder.get_object('vnc_client_entry'),
            'rdp_entry': self.builder.get_object('rdp_client_entry'),
            'telnet_entry': self.builder.get_object('telnet_client_entry'),
            'ftp_entry': self.builder.get_object('ftp_client_entry'),
            'vnc_embedded_chkbutton': self.builder.get_object('vnc_embedded_chkbutton')}

        events = {
            'on_dialog_preferences_close': self.close_event,
            'on_pref_cancel_button_clicked': self.close_event,
            'on_pref_appy_button_clicked': self.apply_event,
            'on_vnc_embedded_chkbutton_toggled': self.toggle_vnc_embeded,
            'on_ssh_client_entry_changed': self.event_binary_client_changed,
            'on_ftp_client_entry_changed': self.event_binary_client_changed,
            'on_telnet_client_entry_changed': self.event_binary_client_changed,
            'on_vnc_client_entry_changed': self.event_binary_client_changed,
            'on_rdp_client_entry_changed': self.event_binary_client_changed,
            }
        self.builder.connect_signals(events)
        self.fill_controls()
        
    def event_binary_client_changed(self, widget):
        self.check_binary_is_valid(widget)

    def close_event(self, widget):
        self.dlg.destroy()
        
    def init_combo(self, items, active_item=None):
        cb = self.widgets['color_scheme_combo']
        cb_index = self.set_model_from_list(cb, constants.color_palletes)
        if active_item:
            active = cb_index[active_item]
            cb.set_active(active)
        return cb
            
    def set_model_from_list(self, cb, items):
        """
            Setup a ComboBox or ComboBoxEntry based on a list of strings. Return
            a map with the items as keys and the index in the store as the
            value: { 'VAL1':0, 'VAL2':1 }
        """           
        model = gtk.ListStore(str)
        index = {}
        j = 0
        for i in items:
            model.append([i])
            index[i] = j 
            j += 1
        cb.set_model(model)
        if type(cb) == gtk.ComboBoxEntry:
            cb.set_text_column(0)
        elif type(cb) == gtk.ComboBox:
            cell = gtk.CellRendererText()
            cb.pack_start(cell, True)
            cb.add_attribute(cell, 'text', 0)
        return index

    def apply_event(self, widget):
        self.save_config()
        self.close_event(None)
        self.response = gtk.RESPONSE_OK

    def toggle_vnc_embeded(self, widget):
        vnc_client = self.widgets['vnc_entry']
        vnc_options = self.widgets['vnc_options_entry']
        if widget.get_active():
            vnc_client.set_sensitive(False)
            vnc_options.set_sensitive(False)
        else:
            vnc_client.set_sensitive(True)
            vnc_options.set_sensitive(True)
            
    def fill_controls(self):
        #General
        pango_font = self.conf.get_font()
        self.widgets['fontbutton'].set_font_name(pango_font.to_string())
        self.widgets['console_char_entry'].set_text(self.conf.get_word_chars())
        self.widgets['buffer_hscale'].set_value(self.conf.get_buffer_size())
        self.init_combo(constants.color_palletes, self.conf.get_pallete_name())
        
        client, options = self.conf.get_ssh_conf()
        self.widgets['ssh_entry'].set_text(client)
        self.check_binary_is_valid(self.widgets['ssh_entry'])
        self.widgets['ssh_options_entry'].set_text(options)
        
        client, options, embedded = self.conf.get_vnc_conf()
        self.widgets['vnc_entry'].set_text(client)
        self.check_binary_is_valid(self.widgets['vnc_entry'])
        self.widgets['vnc_options_entry'].set_text(options)
        self.widgets['vnc_embedded_chkbutton'].set_active(embedded)
        
        client, options = self.conf.get_telnet_conf()
        self.widgets['telnet_entry'].set_text(client)
        self.check_binary_is_valid(self.widgets['telnet_entry'])
        self.widgets['telnet_options_entry'].set_text(options)
        
        client, options = self.conf.get_ftp_conf()
        self.widgets['ftp_entry'].set_text(client)
        self.check_binary_is_valid(self.widgets['ftp_entry'])
        self.widgets['ftp_options_entry'].set_text(options)
        
        client, options = self.conf.get_rdp_conf()
        self.widgets['rdp_entry'].set_text(client)
        self.check_binary_is_valid(self.widgets['rdp_entry'])
        self.widgets['rdp_options_entry'].set_text(options)

    def save_config(self):
        self.conf.set_ssh_conf(self.widgets['ssh_entry'].get_text(), self.widgets['ssh_options_entry'].get_text())
        self.conf.set_ftp_conf(self.widgets['ftp_entry'].get_text(), self.widgets['ftp_options_entry'].get_text())
        self.conf.set_telnet_conf(self.widgets['telnet_entry'].get_text(), self.widgets['telnet_options_entry'].get_text())
        self.conf.set_rdp_conf(self.widgets['rdp_entry'].get_text(), self.widgets['rdp_options_entry'].get_text())
        self.conf.set_vnc_conf(self.widgets['vnc_entry'].get_text(), self.widgets['vnc_options_entry'].get_text(), str(self.widgets['vnc_embedded_chkbutton'].get_active()))
        self.conf.set_font(self.get_font())
        self.conf.set_pallete_name(self.widgets['color_scheme_combo'].get_active_text())
        self.conf.set_buffer_size(self.widgets['buffer_hscale'].get_value())
        self.conf.set_word_chars(self.widgets['console_char_entry'].get_text())
        self.conf.save_config()
        
    def get_font(self):
        return self.widgets['fontbutton'].get_font_name()
    
    def check_binary_is_valid(self, widget):
        bin_path = widget.get_text()
        if os.path.exists(bin_path):
            widget.modify_base(gtk.STATE_NORMAL, self.default_color)
        else:
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(constants.default_error_color))
            
    def run(self):
        self.dlg.run()