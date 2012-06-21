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
import gobject
import pygtk
pygtk.require("2.0")

from mcm.common.connections import *
from mcm.common.utils import *
from mcm.common.export import *
from mcm.common.configurations import McmConfig
import mcm.common.constants

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

    def __init__(self, aliases, groups, types, cx=None):
        #I need a list with the aliases so I can validate the name
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
                        'on_button_save_clicked': self.save_event,
                        'on_alias_entry1_changed': self.validate_alias,
                        'on_types_combobox_changed': self.insert_default_options,
                }
        self.builder.connect_signals(events)

        # Glade3 changes the behaviour of the comboboxentry widget.

        g_entry = self.widgets['group_combobox'].get_child()
        self.widgets['group_entry1'] = g_entry

        if cx:
            self.aliases.remove(cx.alias)
            self.init_combos(groups, types, cx.group, cx.get_type())
            self.fill_fields(cx)
        else:
            self.init_combos(groups, types)

    def run(self):
        dlg = self.widgets['dlg']
        dlg.run()
        dlg.destroy()

    def init_combos(self, groups, types, active_grp=None, active_type=None):
        cb_groups = self.widgets['group_combobox']
        cb_types = self.widgets['types_combobox']
        grp_index = self.set_model_from_list(cb_groups, groups)
        types_index = self.set_model_from_list(cb_types, types)
        if active_grp and active_type:
            active = grp_index[active_grp]
            cb_groups.set_active(active)
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
        type = widget.get_active_text()
        conf = McmConfig()
        config = ""
        if type == 'SSH':
            not_used, config = conf.get_ssh_conf()
        elif type == 'VNC':
            not_used, config = conf.get_vnc_conf()
        elif type == 'RDP':
            not_used, config = conf.get_rdp_conf()
        elif type == 'TELNET':
            not_used, config = conf.get_telnet_conf()
        elif type == 'FTP':
            not_used, config = conf.get_ftp_conf()

        opts_entry = self.widgets['options_entry1']
        opts_entry.set_text(config)

    def cancel_event(self, widget):
        pass

    def save_event(self, widget):
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
            widget.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#FFADAD"))
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
    CSV = 1
    HTML = 2
    DIR = 3

    def __init__(self, model=0):
        self.response = gtk.RESPONSE_CANCEL
        self.error = None
        self.uri = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_file_utils)
        self.dlg = self.builder.get_object('select_file_dialog')

        events = {
                  'on_open_button7_clicked': self.open_event,
                  'on_cancel_button6_clicked': self.cancel_event,
                }
        self.builder.connect_signals(events)
        self.attach_filter(model)

    def attach_filter(self, model):
        _filter = gtk.FileFilter()
        if model is FileSelectDialog.CSV:
            _filter.set_name("CSV")
            _filter.add_pattern("*.csv")
        elif model is FileSelectDialog.HTML:
            _filter.set_name("HTML")
            _filter.add_mime_type("text/html")
            _filter.add_pattern("*.html")
            _filter.add_pattern("*.htm")
        self.dlg.add_filter(_filter)

        _filter = gtk.FileFilter()
        _filter.set_name(constants.all_connections_filter_name)
        _filter.add_pattern("*")
        self.dlg.add_filter(_filter)
                

    def get_response(self):
        return self.response

    def open_event(self, widget):
        self.uri = self.dlg.get_filename()
        self.response = gtk.RESPONSE_OK

    def cancel_event(self, widget):
        self.response = gtk.RESPONSE_CANCEL

    def get_filename(self):
        return self.uri

    def run(self):
        self.dlg.run()
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
            'on_vnc_embedded_chkbutton_toggled': self.toggle_vnc_embeded}
        self.builder.connect_signals(events)
        self.fill_controls()

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
        self.widgets['ssh_options_entry'].set_text(options)
        
        client, options, embedded = self.conf.get_vnc_conf()
        self.widgets['vnc_entry'].set_text(client)
        self.widgets['vnc_options_entry'].set_text(options)
        self.widgets['vnc_embedded_chkbutton'].set_active(embedded)
        
        client, options = self.conf.get_telnet_conf()
        self.widgets['telnet_entry'].set_text(client)
        self.widgets['telnet_options_entry'].set_text(options)
        
        client, options = self.conf.get_ftp_conf()
        self.widgets['ftp_entry'].set_text(client)
        self.widgets['ftp_options_entry'].set_text(options)
        
        client, options = self.conf.get_rdp_conf()
        self.widgets['rdp_entry'].set_text(client)
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
    
    def run(self):
        self.dlg.run()


class McmCheckbox(gtk.HBox):

    def __init__(self, title):
        gtk.HBox.__init__(self, False)
        self._label = gtk.Label(title)
        self._current_alias = title
        self.pack_start(self._label, True, True, 0)
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
        self.hide_checkbox()

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


class McmNewTipDialog(object):

    def __init__(self):
        self.response = gtk.RESPONSE_CANCEL
        self.new_tip = None
        self.error = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_tips)
        self.widgets = {
                        'dlg': self.builder.get_object('new_tips_dialog'),
                        'section_entry': self.builder.get_object('section_entry'),
                        'subsection_entry': self.builder.get_object('subsection_entry'),
                        'name_entry': self.builder.get_object('name_entry'),
                        'value_entry': self.builder.get_object('value_entry'),
                        'send_checkbox': self.builder.get_object('send_checkbox'),
                        }
        events = {
                        'response': self.cancel_event,
                        'on_cancel_button_clicked': self.cancel_event,
                        'on_save_button_clicked': self.save_event,
                        'on_help_button_clicked': self.help_event,
                }
        self.builder.connect_signals(events)
        self.dlg = self.widgets['dlg']

    def run(self):
        self.dlg.run()

    def cancel_event(self, widget):
        self.response = gtk.RESPONSE_CANCEL
        self.dlg.destroy()
        return True

    def save_event(self, widget):
        self.response = gtk.RESPONSE_OK
        section = self.widgets['section_entry'].get_text()
        subsection = self.widgets['subsection_entry'].get_text()
        name = self.widgets['name_entry'].get_text()
        value = self.widgets['value_entry'].get_text()
        send = self.widgets['send_checkbox'].get_active()

        # Shall I add a "Are you sure" dialog when sending to google docs?

        self.new_tip = Tip(0, section, subsection, name, value)
        self.dlg.destroy()
        return True

    def help_event(self, widget):
        dlg = UtilityDialogs()
        response = dlg.show_info_dialog(constants.send_world, constants.google_docs_disclaimer)


class McmMenu(gtk.Menu):

    def __init__(self, label):
        gtk.Menu.__init__(self)
        self.label = label


class TipGtkMenuItem(gtk.MenuItem):

    def __init__(self, label, tip):
        gtk.MenuItem.__init__(self, label)
        self.tip = tip


class McmTipsWidget(object):

    def __init__(self, hbox):
        self.tips = Tips()
        self.tips_list = self.tips.read()
        self.hbox = hbox
        self.menu_bar = self.hbox.get_children()[0]
        self.tips_entry = self.hbox.get_children()[1]
        self.tips_entry.connect("icon-press", self.entry_icon_event)
        self.draw_menu_bar()

    def draw_menu_bar(self):
        root_menu_item = self.menu_bar.get_children()[0]
        sections_menu = gtk.Menu()
        root_menu_item.set_submenu(sections_menu)
        for sect in self.draw_sections():
            menu = sect.get_submenu()
            for subsect in self.draw_subsections(menu):
                menu.append(subsect)
                sub_menu = subsect.get_submenu()
                for tips in self.draw_tips_menu(menu, sub_menu):
                    sub_menu.append(tips)
            sections_menu.append(sect)

    def entry_icon_event(self, widget, icon, event):
        # Using 'event.button' I can know which mouse button was used
        if icon.value_name == "GTK_ENTRY_ICON_PRIMARY":
            print "To Console"
        elif icon.value_name == "GTK_ENTRY_ICON_SECONDARY":
            new_tip_dialog = McmNewTipDialog()
            new_tip_dialog.run()
            if new_tip_dialog.response == gtk.RESPONSE_OK:
                self.tips_list.append(new_tip_dialog.new_tip)
                self.draw_menu_bar()
                self.tips.save(self.tips_list)
        return True

    def draw_sections(self):
        sections = []
        menu_items = []
        for tip in self.tips_list:
            sections.append(tip.section)
        sections = set(sections)
        for section in sections:
            mi = gtk.MenuItem(section)
            me = McmMenu(section)
            mi.set_submenu(me)
            mi.show()
            menu_items.append(mi)
        return menu_items

    def draw_subsections(self, sections_menu):
        subsections = []
        menu_items = []
        label = sections_menu.label
        for tip in self.tips_list:
            if label == tip.section:
                subsections.append(tip.subsection)
        subsections = set(subsections)
        for subsection in subsections:
            mi = gtk.MenuItem(subsection)
            me = McmMenu(subsection)
            mi.set_submenu(me)
            mi.show()
            menu_items.append(mi)
        return menu_items

    def draw_tips_menu(self, sections_menu, subsections_menu):
        tips = []
        menu_items = []
        sect_label = sections_menu.label
        subsect_label = subsections_menu.label
        for tip in self.tips_list:
            if subsect_label == tip.subsection and sect_label == tip.section:
                tips.append(tip)
        for tip in tips:
            mi = TipGtkMenuItem(tip.name, tip)
            mi.connect("activate", self.item_event)
            mi.show()
            menu_items.append(mi)
        return menu_items

    def draw_breadcrumb(self, tip):
        items = self.menu_bar.get_children()
        if len(items) > 1:
            self.menu_bar.remove(items[1])
            self.menu_bar.remove(items[2])
            self.menu_bar.remove(items[3])

        mi_section = gtk.MenuItem(tip.section)
        mi_subsection = gtk.MenuItem(tip.subsection)
        mi_name = gtk.MenuItem(tip.name)

        mi_section.show()
        mi_subsection.show()
        mi_name.show()

        sect_menu = McmMenu(tip.section)
        subsect_menu = McmMenu(tip.subsection)
        name_menu = McmMenu(tip.name)

        for sect in self.draw_sections():
            menu = sect.get_submenu()
            for subsect in self.draw_subsections(menu):
                menu.append(subsect)
                sub_menu = subsect.get_submenu()
                for tips in self.draw_tips_menu(menu, sub_menu):
                    sub_menu.append(tips)
            sect_menu.append(sect)

        for subsect in self.draw_subsections(sect_menu):
            subsect_menu.append(subsect)
            sub_menu = subsect.get_submenu()
            for tips in self.draw_tips_menu(sect_menu, sub_menu):
                sub_menu.append(tips)

        for tips in self.draw_tips_menu(sect_menu, subsect_menu):
            name_menu.append(tips)

        mi_section.set_submenu(sect_menu)
        mi_subsection.set_submenu(subsect_menu)
        mi_name.set_submenu(name_menu)

        self.menu_bar.append(mi_section)
        self.menu_bar.append(mi_subsection)
        self.menu_bar.append(mi_name)

    def item_event(self, widget):
        self.draw_breadcrumb(widget.tip)
        self.tips_entry.set_text(widget.tip.value)

    def update(self, filename=None):
        response = self.tips.update(filename)
        self.tips_list = self.tips.read()
        self.draw_menu_bar()
        return response

class ManageConnectionsDialog(object):

    def __init__(self, connections, groups, types):
        self.response = gtk.RESPONSE_CANCEL
        self.connections = connections
        self.groups = groups
        self.types = types
        self.active_column = None
        builder = gtk.Builder()
        builder.add_from_file(constants.glade_edit_cx)
        self.dialog = builder.get_object("edit_connections_dialog")
        self.tree_container = builder.get_object("tree_scroll")
        events = {
                        'response': self.cancel_event,
                        'on_cancel_button_clicked': self.cancel_event,
                        'on_save_button_clicked': self.save_event,
                        'on_exp_csv_button_clicked': self.export_csv_event,
                        'on_exp_html_button_clicked': self.export_html_event,
                }
        builder.connect_signals(events)
        self.draw_tree()

    def draw_tree(self):
        self.view = self.connections_view()
        self.tree_container.add(self.view)
        self.tree_container.show_all()

    def redraw_tree(self):
        self.tree_container.remove(self.view)
        self.draw_tree()

    def run(self):
        self.dialog.run()

    def destroy(self):
        self.dialog.destroy()
    
    def cancel_event(self, widget):
        self.response = gtk.RESPONSE_CANCEL

    def save_event(self, widget):
        self.response = gtk.RESPONSE_OK

    def export_csv_event(self, widget):
        dlg = FileSelectDialog(FileSelectDialog.CSV)
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            _csv = ExportCsv(dlg.get_filename(), self.connections)
            idlg = UtilityDialogs()
            idlg.show_info_dialog(constants.export_csv, constants.saved_file % dlg.get_filename())

    def export_html_event(self, widget):
        dlg = FileSelectDialog(FileSelectDialog.HTML)
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            _html = Html(dlg.get_filename(), constants.version, self.connections)
            _html.export()
            idlg = UtilityDialogs()
            idlg.show_info_dialog(constants.export_html, constants.saved_file % dlg.get_filename())

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
        return index

    def get_selection(self):
        cursor = self.view.get_selection()
        model = self.view.get_model()
        (model, iter) = cursor.get_selected()
        if iter == None:
            return None
        alias = model.get_value(iter, 0)
        return alias

    def cell_edited_event(self, widget, path, new_value, store):
        col_title = self.active_column.get_title()
        alias = self.get_selection()
        acx = self.connections[alias]
        if col_title == constants.col_title_user:
            acx.user = new_value 
        elif col_title == constants.col_title_pwd:
            acx.password = new_value 
        elif col_title == constants.col_title_host:
            acx.host = new_value 
        elif col_title == constants.col_title_port:
            acx.port = new_value 
        elif col_title == constants.col_title_desc:
            acx.description = new_value 
        elif col_title == constants.col_title_opts:
            acx.options = new_value 

        self.connections[alias] = acx
        self.redraw_tree()

    def cell_combo_event(self, widget, path, new_iter):
        """Method called when a change on a combobox happens"""
        new_value = widget.props.model.get_value(new_iter, 0)
        col_title = self.active_column.get_title()
        alias = self.get_selection()
        acx = self.connections[alias]

        if col_title == constants.col_title_group:
            acx.group = new_value 
        elif col_title == constants.col_title_type:
            acx = connections_factory(new_value,  acx.user, acx.host, acx.alias, acx.password, acx.port, acx.group, acx.options, acx.description)
        
        self.connections[alias] = acx
        self.redraw_tree()

    def cell_click_event(self, widget, event, store):
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        #row = int(path[0][0])
        self.active_column = path[1]
        col_title = self.active_column.get_title()
        if col_title == constants.col_title_delete and event.type == gtk.gdk._2BUTTON_PRESS:
            alias = self.get_selection()
            dlg = UtilityDialogs()
            response = dlg.show_question_dialog(constants.deleting_connection_warning % alias, constants.are_you_sure)
            if response == gtk.RESPONSE_OK:
                del self.connections[alias]
                self.redraw_tree()

    def connections_view(self):
        store = self.connections_model()
        view = gtk.TreeView(store)

        for column in self.generate_columns(store):
            view.append_column(column)

        # Configure Tree Properties
        view.set_headers_clickable(True)
        view.set_rules_hint(True)
        view.set_search_column(0)
        view.set_fixed_height_mode(True)
        view.connect('button-press-event', self.cell_click_event, store )

        return view

    def generate_columns(self, store):
        columns = []
        alias_renderer = gtk.CellRendererText()

        renderer0 = gtk.CellRendererText()
        renderer0.set_property( 'editable', True)
        renderer0.connect('edited', self.cell_edited_event, store )
        img_renderer = gtk.CellRendererPixbuf()

        # We create the CellRendererCombo with the given models and then feed this models to the event
        types_combo_renderer = self.init_combo(self.types)
        types_combo_renderer.connect('changed', self.cell_combo_event)
        groups_combo_renderer = self.init_combo(self.groups)
        groups_combo_renderer.connect('changed', self.cell_combo_event)

        # Make the first row sortable
        col = gtk.TreeViewColumn(constants.col_title_alias, alias_renderer, text=0)
        col.set_sort_column_id(0)
        columns.append(col)

        columns.append(gtk.TreeViewColumn(constants.col_title_type, types_combo_renderer, text=1))
        columns.append(gtk.TreeViewColumn(constants.col_title_group, groups_combo_renderer, text=8))
        columns.append(gtk.TreeViewColumn(constants.col_title_user, renderer0, text=5))
        columns.append(gtk.TreeViewColumn(constants.col_title_host, renderer0, text=3))
        columns.append(gtk.TreeViewColumn(constants.col_title_port, renderer0, text=4))
        columns.append(gtk.TreeViewColumn(constants.col_title_opts, renderer0, text=7))
        columns.append(gtk.TreeViewColumn(constants.col_title_pwd, renderer0, text=6))

        # The Delete column looks awful when we maximize the dialog. So we expand this one instead
        desc_col = gtk.TreeViewColumn(constants.col_title_desc, renderer0, text=9)
        desc_col.set_expand(True)
        columns.append(desc_col)
        columns.append(gtk.TreeViewColumn(constants.col_title_delete, img_renderer, pixbuf=10))

        return columns

    def connections_model(self):
        """Creates a ListStore with the Connections data"""
        store = gtk.ListStore(str, str, str, str, str, str, str, str, str, str, gtk.gdk.Pixbuf)
        img = self.dialog.render_icon(gtk.STOCK_CLEAR, gtk.ICON_SIZE_BUTTON)

        for cx in self.connections.values():
            cx_list = cx.to_list()
            cx_list.append(img)
            store.append(cx_list)
        return store

class HttpServerDialog(object):
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file(constants.glade_http)
        self.dialog = builder.get_object("http_server_dialog")
        self.dialog.connect('on_http_server_connect_toggled', self.start_server)
        self.dialog.connect('on_http_server_disconnect_toggled', self.stop_server)
        #self.http_server = McmHttpServerThread

    def run(self):
        self.dialog.run()
        self.dialog.destroy()

    def start_server(self):
        pass

    def stop_server(self):
        pass

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
