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

import gtk
import mcm.common.configurations
import mcm.common.connections

from mcm.common import constants
from mcm.gui.widgets import DefaultColorSettings

class AddConnectionDialog(object):

    def __init__(self, cx=None, selected_group=None):
        connections = mcm.common.connections.ConnectionStore()
        connections.load()
        self.aliases = connections.get_aliases()
        
        self.response = gtk.RESPONSE_CANCEL
        self.default_color = DefaultColorSettings().base_color
        self.new_connection = None
        self.error = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_new_cx)
        
        self.widgets = {
                        'dlg': self.builder.get_object('dialog_add'),
                        'types_combobox': self.builder.get_object('types_combobox'),
                        'group_combobox': self.builder.get_object('group_combobox'),
                        'user_entry1': self.builder.get_object('user_entry1'),
                        'host_entry1': self.builder.get_object('host_entry1'),
                        'port_entry1': self.builder.get_object('port_entry1'),
                        'options_entry1': self.builder.get_object('options_entry1'),
                        'description_entry1': self.builder.get_object('description_entry1'),
                        'password_entry1': self.builder.get_object('password_entry1'),
                        'alias_entry1': self.builder.get_object('alias_entry1'),
                        'title_label': self.builder.get_object('title_label'),
                        }
        events = {
                        'response': self.cancel_event,
                        'on_button_cancel_clicked': self.cancel_event,
                        'on_button_save_clicked': self.event_save,
                        'on_alias_entry1_changed': self.validate_alias,
                        'on_types_combobox_changed': self.insert_default_options,
                }
        self.builder.connect_signals(events)

        g_entry = self.widgets['group_combobox'].get_child()
        self.widgets['group_entry1'] = g_entry


        groups = connections.get_groups()
        if cx:
            self.aliases.remove(cx.alias)
            self.init_combos(groups, cx.group, cx.get_type())
            self.fill_fields(cx)
        else:
            self.init_combos(groups, selected_group)

    def run(self):
        dlg = self.widgets['dlg']
        dlg.run()
        dlg.destroy()

    def init_combos(self, groups, active_grp=None, active_type=None):
        cb_groups = self.widgets['group_combobox']
        cb_types = self.widgets['types_combobox']
        grp_index = self.set_model_from_list(cb_groups, groups)
        types_index = self.set_model_from_list(cb_types, mcm.common.connections.types)
        if active_grp:
            active = grp_index[active_grp]
            cb_groups.set_active(active)
        if active_type:
            active = types_index[active_type]
            cb_types.set_active(active)

    def set_model_from_list(self, cb, items):
        """Setup a ComboBox or ComboBoxEntry based on a list of strings."""           
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

    def insert_default_options(self, widget):
        cx_type = widget.get_active_text()
        conf = mcm.common.configurations.McmConfig()
        config = ""
        if cx_type == 'SSH':
            config = conf.get_ssh_conf()[1]
        elif cx_type == 'VNC':
            config = conf.get_vnc_conf()[1]
        elif cx_type == 'RDP':
            config = conf.get_rdp_conf()[1]
        elif cx_type == 'TELNET':
            config = conf.get_telnet_conf()[1]
        elif cx_type == 'FTP':
            config = conf.get_ftp_conf()[1]

        opts_entry = self.widgets['options_entry1']
        opts_entry.set_text(config)
        
        port_entry = self.widgets['port_entry1']
        port_entry.set_text(str(mcm.common.connections.types[cx_type]))

    def cancel_event(self, widget):
        pass

    def event_save(self, widget):
        if self.error == None:
            self.response = gtk.RESPONSE_OK
            cx_map = {}
            cx_map['type'] = self.widgets['types_combobox'].get_active_text()
            cx_map['group'] = self.widgets['group_entry1'].get_text()
            cx_map['user'] = self.widgets['user_entry1'].get_text()
            cx_map['host'] = self.widgets['host_entry1'].get_text()
            cx_map['alias'] = self.widgets['alias_entry1'].get_text()
            cx_map['port'] = self.widgets['port_entry1'].get_text()
            cx_map['description'] = self.widgets['description_entry1'].get_text()
            cx_map['password'] = self.widgets['password_entry1'].get_text()
            cx_map['options'] = self.widgets['options_entry1'].get_text()
            self.new_connection = mcm.common.connections.mapped_connections_factory(cx_map)

    def validate_alias(self, widget):
        alias = widget.get_text()
        if alias in self.aliases:
            self.error = constants.alias_error
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse(constants.default_error_color))
            widget.set_tooltip_text(self.error)
        else:
            self.error = None
            widget.modify_base(gtk.STATE_NORMAL, self.default_color)
            widget.set_tooltip_text(constants.alias_tooltip)

    def validate_port(self, widget):
        pass
    
    def fill_fields(self, cx):
        """Fill the dialog fields so we can use it to edit a connection"""
        user = self.widgets['user_entry1']
        host = self.widgets['host_entry1']
        alias = self.widgets['alias_entry1']
        port = self.widgets['port_entry1']
        desc = self.widgets['description_entry1']
        fpass = self.widgets['password_entry1']
        options = self.widgets['options_entry1']

        user.set_text(cx.user)
        host.set_text(cx.host) 
        alias.set_text(cx.alias)
        port.set_text(cx.port)
        desc.set_text(cx.description)
        fpass.set_text(cx.password)
        options.set_text(cx.options)