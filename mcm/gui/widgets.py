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

import os
import gtk
import pygtk
pygtk.require("2.0")

from mcm.common.connections import connections_factory, types, ConnectionStore
from mcm.common.export import print_csv, Html
from mcm.common.configurations import McmConfig
import mcm.common.constants as constants

'''
Dialogs for MCM Connections Manager
'''

class UtilityDialogs(object):
    """
    Class that defines the methods used to display MessageDialog dialogs
    to the user
    """

    def __init__(self):
        pass

    def show_question_dialog(self, title, message):
        """Display a Warning Dialog and return the response to the caller"""
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, title)
        dialog.format_secondary_text(message)
        response = dialog.run()
        dialog.destroy()
        return response

    def show_error_dialog(self, title, message):
        """Display an error dialog to the user"""
        self.show_common_dialog(title, message, gtk.MESSAGE_ERROR)

    def show_info_dialog(self, title, message):
        """Display an error dialog to the user"""
        self.show_common_dialog(title, message, gtk.MESSAGE_INFO)

    def show_common_dialog(self, title, message, icon):
        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, icon, gtk.BUTTONS_OK, title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


class AddConnectionDialog(object):

    def __init__(self, aliases, groups, types, cx=None, selected_group=None):
        self.response = gtk.RESPONSE_CANCEL
        self.default_color = DefaultColorSettings().base_color
        self.new_connection = None
        self.error = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_new_cx)
        self.aliases = aliases
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

        if cx:
            self.aliases.remove(cx.alias)
            self.init_combos(groups, types, cx.group, cx.get_type())
            self.fill_fields(cx)
        else:
            self.init_combos(groups, types, selected_group)

    def run(self):
        dlg = self.widgets['dlg']
        dlg.run()
        dlg.destroy()

    def init_combos(self, groups, types, active_grp=None, active_type=None):
        cb_groups = self.widgets['group_combobox']
        cb_types = self.widgets['types_combobox']
        grp_index = self.set_model_from_list(cb_groups, groups)
        types_index = self.set_model_from_list(cb_types, types)
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
        conf = McmConfig()
        config = ""
        if cx_type == 'SSH':
            not_used, config = conf.get_ssh_conf()
        elif cx_type == 'VNC':
            not_used, config, embedded = conf.get_vnc_conf()
        elif cx_type == 'RDP':
            not_used, config = conf.get_rdp_conf()
        elif cx_type == 'TELNET':
            not_used, config = conf.get_telnet_conf()
        elif cx_type == 'FTP':
            not_used, config = conf.get_ftp_conf()

        opts_entry = self.widgets['options_entry1']
        opts_entry.set_text(config)
        
        port_entry = self.widgets['port_entry1']
        port_entry.set_text(str(types[cx_type]))

    def cancel_event(self, widget):
        pass

    def event_save(self, widget):
        if self.error == None:
            self.response = gtk.RESPONSE_OK
            cx_type = self.widgets['types_combobox'].get_active_text()
            cx_group = self.widgets['group_entry1'].get_text()
            cx_user = self.widgets['user_entry1'].get_text()
            cx_host = self.widgets['host_entry1'].get_text()
            cx_alias = self.widgets['alias_entry1'].get_text()
            cx_port = self.widgets['port_entry1'].get_text()
            cx_desc = self.widgets['description_entry1'].get_text()
            cx_pass = self.widgets['password_entry1'].get_text()
            cx_options = self.widgets['options_entry1'].get_text()
            self.new_connection = connections_factory(cx_type, cx_user, cx_host, cx_alias, cx_pass, cx_port, cx_group, cx_options, cx_desc)

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
        _filter.set_name("CSV")
        _filter.add_mime_type("text/csv")
        _filter.add_pattern("*.csv")
        self.dlg.add_filter(_filter)
        
        if is_export:
            _filter = gtk.FileFilter()
            _filter.set_name("HTML")
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
        self.dlg.get_filter()

    def run(self):
        self.response = self.dlg.run()
        self.uri = self.dlg.get_filename()
        self.mime = self.dlg.get_filter().get_name().lower()
        self.dlg.destroy()

class ImportProgressDialog(object):

    def __init__(self, cxs, aliases):
        self.aliases = aliases
        self.connections = {}
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_import)
        self.dlg = self.builder.get_object('import_progress')
        self.results = self.builder.get_object('import_result')
        events = {
                    'on_ok_button6_clicked': self.close_event,
                    'on_import_progress_destroy': self.close_event,
                }
        self.builder.connect_signals(events)
        for d in cxs:
            alias = d['alias'].strip()
            if len(d) != 10 or alias in self.aliases:
                self.write_result(constants.import_not_saving % alias)
                continue
            cx = connections_factory(d['type'], d['user'],
                                    d['host'], alias, d['password'], d['port'],
                                    d['group'], d['options'], d['description'])
            self.connections[alias] = cx
            self.write_result(constants.import_saving % cx)

    def run(self):
        self.dlg.run()

    def close_event(self, widget=None):
        self.dlg.destroy()

    def write_result(self, text):
        buf = self.results.get_buffer()
        if buf == None:
            buf = gtk.TextBuffer()
            self.results.set_buffer(buf)
        buf.insert_at_cursor(text)


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
        return self._button.get_active()
    
    def hide_checkbox(self):
        self._button.hide()
        
    def show_checkbox(self):
        self._button.show()

    def set_title(self, title):
        self._label.set_text(title)

    def get_title(self):
        return self._label.get_text()

    def get_current_alias(self):
        return self._current_alias

class McmMenu(gtk.Menu):

    def __init__(self, label):
        gtk.Menu.__init__(self)
        self.label = label


class TipGtkMenuItem(gtk.MenuItem):

    def __init__(self, label, tip):
        gtk.MenuItem.__init__(self, label)
        self.tip = tip

class ManageConnectionsDialog(object):

    def __init__(self):
        self.response = gtk.RESPONSE_CANCEL
        self.connections = ConnectionStore()
        self.connections.load()
        self.groups = self.connections.get_groups()
        self.types = types.keys()
        self.cell_edited_color = DefaultColorSettings().tooltip_fg_color
        builder = gtk.Builder()
        builder.add_from_file(constants.glade_edit_cx)
        self.dialog = builder.get_object("edit_connections_dialog")
        self.tree_container = builder.get_object("tree_scroll")
        events = {
                        'response': self.cancel_event,
                        'on_cancel_button_clicked': self.cancel_event,
                        'on_save_button_clicked': self.event_save,
                        'on_exp_html_button_clicked': self.event_export,
                }
        builder.connect_signals(events)
        self.draw_tree()

    def draw_tree(self):
        self.view = self.connections_view()
        self.tree_container.add(self.view)
        self.tree_container.show_all()

    def run(self):
        self.dialog.run()

    def destroy(self):
        self.dialog.destroy()
    
    def cancel_event(self, widget):
        self.response = gtk.RESPONSE_CANCEL

    def event_save(self, widget):
        self.response = gtk.RESPONSE_OK
        self.connections.save()

    def event_export(self, widget):
        dlg = FileSelectDialog(True)
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK and dlg.mime == 'html':
            _html = Html(constants.version, self.connections)
            _html.export(dlg.get_filename())
            idlg = UtilityDialogs()
            idlg.show_info_dialog(constants.export_finished, constants.saved_file % dlg.get_filename())
        elif dlg.response == gtk.RESPONSE_OK and dlg.mime == 'csv':
            _csv = print_csv(self.connections, dlg.get_filename())
            idlg = UtilityDialogs()
            idlg.show_info_dialog(constants.export_finished, constants.saved_file % dlg.get_filename())

    def init_combo(self, items, active_item=None):
        cb = gtk.CellRendererCombo()
        cb_index = self.set_model_from_list(cb, items)
        if active_item:
            active = cb_index[active_item]
            cb.set_active(active)
        return cb

    def set_model_from_list(self, cb, items):
        """Setup a CellRendererCombo based on a list of strings."""           
        model = gtk.ListStore(str)
        index = {}
        j = 0
        for i in items:
            model.append([i])
            index[i] = j
            j += 1
        cb.set_property('model', model)
        cb.set_property('text-column', 0)
        cb.set_property('editable', True)
        cb.set_property('has-entry', False)
        return index

    def type_edited_event(self, widget, path, new_iter, model):
        self.update_combo_cell(widget, path, 1, new_iter, model)
    
    def group_edited_event(self, widget, path, new_iter, model):
        self.update_combo_cell(widget, path, 7, new_iter, model)
    
    def update_cell(self, widget, pos_x, new_value, model):
        pos_y = widget.pos_y
        model[pos_x][pos_y] = new_value
        alias = model[pos_x][0]
        cx = self.connections.get(alias)
        if pos_y is 4:
            cx.user = new_value
        elif pos_y is 2:
            cx.host = new_value
        elif pos_y is 3:
            cx.port = new_value
        elif pos_y is 6:
            cx.options = new_value
        elif pos_y is 5:
            cx.password = new_value
        elif pos_y is 8:
            cx.description = new_value
        
        self.connections.update(alias, cx)
        
    def update_combo_cell(self, widget, pos_x, pos_y, new_iter, model):
        new_value = widget.props.model.get_value(new_iter, 0)
        model[pos_x][pos_y] = new_value
        alias = model[pos_x][0]
        cx = self.connections.get(alias)
        if pos_y is 1:
            cx = connections_factory(new_value, 
                                     cx.user, 
                                     cx.host, 
                                     cx.alias, 
                                     cx.password, 
                                     cx.port, 
                                     cx.group, 
                                     cx.options, 
                                     cx.description)
        elif pos_y is 7:
            cx.group = new_value
            
        self.connections.update(alias, cx)

    def cell_click_event(self, widget, event):
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        active_column = path[1]
        col_title = active_column.get_title()
        if col_title == constants.col_title_delete and event.type == gtk.gdk._2BUTTON_PRESS:
            cursor = widget.get_selection()
            (model, a_iter) = cursor.get_selected()
            alias = model.get_value(a_iter, 0)
            dlg = UtilityDialogs()
            response = dlg.show_question_dialog(constants.deleting_connection_warning % alias, constants.are_you_sure)
            if response == gtk.RESPONSE_OK:
                model.remove(a_iter)
                self.connections.delete(alias)

    def connections_view(self):
        store = self.connections_model()
        view = gtk.TreeView(store)

        for column in self.generate_columns(store):
            view.append_column(column)

        # Configure Tree Properties
        view.set_headers_clickable(True)
        view.set_rules_hint(True)
        view.set_search_column(0)
        #view.set_fixed_height_mode(True)
        view.columns_autosize()
        view.connect('button-press-event', self.cell_click_event)

        return view

    def generate_columns(self, store):
        columns = []
        
        # For each column we need a renderer so we can easily pick the cell value
        alias_renderer = gtk.CellRendererText()

        # We create the CellRendererCombo with the given models and then feed this models to the event
        types_combo_renderer = self.init_combo(self.types)
        types_combo_renderer.connect('changed', self.type_edited_event, store)
        types_combo_renderer.pos_y = 1
        
        groups_combo_renderer = self.init_combo(self.groups)
        groups_combo_renderer.connect('changed', self.group_edited_event, store)
        groups_combo_renderer.pos_y = 7
        
        user_renderer = self.get_new_cell_renderer(True, 4, store)
        host_renderer = self.get_new_cell_renderer(True, 2, store)
        port_renderer = self.get_new_cell_renderer(True, 3, store)
        opts_renderer = self.get_new_cell_renderer(True, 6, store)
        pwd_renderer = self.get_new_cell_renderer(True, 5, store)
        desc_renderer = self.get_new_cell_renderer(True, 8, store)
        
        # Renderer for the delete button
        img_renderer = gtk.CellRendererPixbuf()
        
        # Make the first row sortable
        col = gtk.TreeViewColumn(constants.col_title_alias, alias_renderer, text=0)
        col.set_sort_column_id(0)
        col.set_resizable(True)
        col.set_expand(True)
        
        columns.append(col)
        columns.append(self.get_new_column(constants.col_title_type, types_combo_renderer))
        columns.append(self.get_new_column(constants.col_title_group, groups_combo_renderer))
        columns.append(self.get_new_column(constants.col_title_user, user_renderer))
        columns.append(self.get_new_column(constants.col_title_host, host_renderer))
        columns.append(self.get_new_column(constants.col_title_port, port_renderer))
        columns.append(self.get_new_column(constants.col_title_opts, opts_renderer))
        columns.append(self.get_new_column(constants.col_title_pwd, pwd_renderer))
        columns.append(self.get_new_column(constants.col_title_desc, desc_renderer))
        
        # Finally we append the delete button column
        del_col = gtk.TreeViewColumn(constants.col_title_delete, img_renderer, pixbuf=9)
        del_col.set_resizable(False)
        del_col.set_expand(False)
        columns.append(del_col)

        return columns

    def connections_model(self):
        """Creates a ListStore with the Connections data"""
        store = gtk.ListStore(str, str, str, str, str, str, str, str, str, gtk.gdk.Pixbuf)
        img = self.dialog.render_icon(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON)
        for cx in self.connections.get_all():
            cx_list = cx.to_list()
            cx_list.append(img)
            store.append(cx_list)
        return store
    
    def get_new_column(self, title, renderer, resizable=False):
        col = gtk.TreeViewColumn(title, renderer, text=renderer.pos_y)
        col.set_resizable(True)
        return col
    
    def get_new_cell_renderer(self, editable, pos_y, store):
        renderer = gtk.CellRendererText()
        renderer.set_property( 'editable', editable)
        renderer.pos_y = pos_y
        renderer.connect('edited', self.update_cell, store )
        return renderer

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
            
class InstallPublicKeyDialog(object):
    
    def __init__(self):
        self.dialog = gtk.Dialog("Installing Public Key", None, 0, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.dialog.set_default_response(gtk.RESPONSE_CLOSE)
        self.dialog.connect("response", self.hide)
        
    def install(self, username, server):
        vbox = self.dialog.get_child()
        pk_path = os.path.expanduser("~") + '/.ssh/id_rsa.pub'
        
        if os.path.exists(pk_path):
            import vte
            scroll = gtk.ScrolledWindow()
            scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            v = vte.Terminal()
            scroll.add(v)
            vbox.add(scroll)
            cx = '%s@%s' % (username, server)
            cmd = ['/usr/bin/ssh-copy-id', cx]
            v.fork_command(cmd[0], cmd, None, None, False, False, False)
            self.dialog.resize(600, 400)
        else:
            label = gtk.Label()
            label.set_text(constants.public_key_rsa_not_found)
            vbox.add(label)
        self.dialog.show_all()
        
    def hide(self, dialog, response_id):
        self.dialog.hide()
