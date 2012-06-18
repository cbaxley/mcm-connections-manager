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

'''
Main Script for mcm gtk
'''

import gtk
import gtk.glade as glade
import vte
import webbrowser
import gettext


from subprocess import Popen
from vnc import MCMVncClient
from mcm.common import constants
from mcm.common.configurations import McmConfig
from mcm.common.connections import ConnectionStore, types
from mcm.common.export import ExportCsv, Html
from mcm.common.utils import Csv
from mcm.gui.widgets import AddConnectionDialog, UtilityDialogs, McmCheckbox, \
    FileSelectDialog, ImportProgressDialog, DefaultColorSettings, \
    ManageConnectionsDialog, PreferencesDialog



for module in glade, gettext:
    module.bindtextdomain('mcm', constants.local_path)
    module.textdomain('mcm')

class MCMGtk(object):

    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file(constants.glade_main)
        self.widgets = self.init_widgets()
        self.builder.connect_signals(self.events())

        # I don't feel like the status icon is a good idea now that mcm is what it is
        # self.init_status_icon(constants.glade_home)

        # self.dao = Dao()
        # self.connections = self.dao.read_xml()
        
        self.connections = ConnectionStore()
        self.connections.load()
        
        self.draw_tree()
        #self.init_tips_menu()
        self.init_main_window()

    def about_event(self, widget):
        about = self.widgets['about']
        about.connect("response", lambda d, r: d.hide())
        about.run()

    def add_event(self, widget):
        dlg = AddConnectionDialog(self.connections.get_aliases(), self.connections.get_groups(), types())
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            cx = dlg.new_connection
            self.connections.add(cx.alias, cx)
            self.draw_tree()

    def assign_key_binding(self, key_binding, callback):
        accel_group = self.widgets['accel_group']
        key, mod = gtk.accelerator_parse(key_binding)
        accel_group.connect_group(key, mod, gtk.ACCEL_VISIBLE, callback)

    def clear_cluster_event(self, widget):
        entry = self.widgets['cluster_entry']
        entry.set_text("")

    def close_tab_event(self, accel_group, window, keyval=None, modifier=None, unk=None):
        terminals = self.widgets['terminals']
        index = terminals.get_current_page()
        terminals.remove_page(index)
        if terminals.get_n_pages() <= 0:
            terminals.hide()
        return True

    def cluster_backspace(self, widget):
        """Call this event when the backspace key is pressed on the entry widget"""
        return self.cluster_send_key('\b')

    def cluster_event(self, widget):
        """Call this event when any key is pressed on the entry widget"""
        command = widget.get_text()
        widget.set_text("")
        if len(command) < 1:
            return False
        return self.cluster_send_key(command)

    def cluster_intro_event(self, widget):
        """Call this event when the enter key is pressed on the entry widget"""
        return self.cluster_send_key('\n')

    def cluster_send_key(self, key):
        """This method is in charge of sending the keys to the selected
        terminals from the entry widget"""
        # Now get the notebook and all the tabs
        cluster_tabs = {}
        terminals = self.widgets['terminals']
        pages = terminals.get_n_pages()
        for i in range(pages):
            scroll = terminals.get_nth_page(i)
            checkbox = terminals.get_tab_label(scroll)
            if checkbox.get_active():
                term = scroll.get_child()
                cluster_tabs[i] = term

        for term in cluster_tabs.values():
            term.feed_child(key)
        return True

    def connect_event(self, widget, path=None, vew_column=None):
        alias = None
        name = gtk.Buildable.get_name(widget)

        if name == 'connect_button' or name == 'mb_connect' or name == 'connections_tree':
            alias = self.get_tree_selection()
        else:
            alias = widget.props.name

        # OMG Someone broke this on GTK 2.17
        #if widget.props.name == 'connect_button' or widget.props.name == 'mb_connect' or widget.props.name == 'connections_tree':
        #    alias = self.get_tree_selection()
        #else:
        #    alias = widget.props.name

        self.do_connect(self.connections.get(alias))

    def delete_event(self, widget):
        alias = self.get_tree_selection()
        dlg = UtilityDialogs()
        response = dlg.show_question_dialog(constants.deleting_connection_warning % alias, constants.are_you_sure)
        if response == gtk.RESPONSE_OK:
            self.connections.delete(alias)
            self.draw_tree()

    def die_term_event(self, scroll, terminals):
        index = terminals.page_num(scroll)
        terminals.remove_page(index)
        if terminals.get_n_pages() <= 0:
            terminals.hide()
        return True

    def die_term_callback(self, term, col, row, data):
        ''' We don't do anything with any of this since we don't have any use for it'''
        return True

    def do_connect(self, connection):
        '''Here I create a ScrolledWindow, attach a VteTerminal widget and all this gets attached
        to a new page on a NoteBook widget. Instead of using a label, I use a custom CheckButton widget
        since the default CheckButton widget covered the whole tab, making it very difficult to switch
        tabs by clicking on them.'''
        # Check for VNC Connections
        if connection:
            if connection.get_type() == "VNC":
                conf = McmConfig()
                client, options, embedded = conf.get_vnc_conf()
                if embedded:
                    return self.vnc_connect(connection)

        #if connection:
            #if connection.get_type() == "RDP":
                #conf = McmConfig()
                #client, options, embedded = conf.get_vnc_conf()
                #if embedded:
                    #return self.rdp_connection(connection)

        # Not VNC continue 
        scroll = gtk.ScrolledWindow()
        # By setting the POLICY_AUTOMATIC, the ScrollWindow resizes itself when hidding the TreeView
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        v = vte.Terminal()
        scroll.add(v)
        terminals = self.widgets['terminals']
        label = None
        menu_label = None
        if connection == None:
            label = McmCheckbox('localhost')
            menu_label = gtk.Label('localhost')
        else:
            label = McmCheckbox(connection.alias)
            label.set_tooltip_text(connection.description)
            menu_label = gtk.Label(connection.alias)
        self.set_window_title(label.get_title())
        index = terminals.append_page_menu(scroll, label, menu_label)
        terminals.set_tab_reorderable(scroll, True)

        # Send the scroll widget to the event so the notebook know which child to close
        v.connect("child-exited", lambda term: self.die_term_event(scroll, terminals))
        v.connect("button-press-event", self.do_popup_console_menu)
        v.connect("key-press-event", self.terminal_key_event)
        v.fork_command()
        if connection != None:
            v.feed_child(connection.gtk_cmd())
        self.assign_key_binding(constants.tabs_switch_keys % (index + 1), self.switch_tab)
        self.assign_key_binding(constants.terminal_copy_keys, self.do_copy)
        self.assign_key_binding(constants.terminal_paste_keys, self.do_paste)
        terminals.show_all()
        terminals.set_current_page(index)
        self.draw_consoles()
        v.grab_focus()

    def do_localhost(self, accel_group, window=None, keyval=None, modifier=None):
        self.do_connect(None)
        return True

    def do_popup_console_menu(self, widget, event):
        '''Draw a Menu ready to be inserted in a vteterminal widget'''
        if event.button == 1:
            return False
        elif event.button == 3:
            menu = gtk.Menu()
            copy = gtk.MenuItem(constants.copy)
            paste = gtk.MenuItem(constants.paste)
            search = gtk.MenuItem(constants.google_search)
            title = gtk.MenuItem(constants.set_title)
            menu.append(copy)
            menu.append(paste)
            menu.append(search)
            menu.append(gtk.SeparatorMenuItem())
            menu.append(title)
            copy.connect('activate', self.do_copy)
            paste.connect('activate', self.do_paste)
            search.connect('activate', self.do_search)
            title.connect('activate', self.do_set_title)
            menu.show_all()
            menu.popup(None, None, None, 3, event.time)
            return True
        else:
            return False

    def do_popup_connections_menu(self, widget, event):
        print "Click!"
        return False

    def do_copy(self, widget, var2=None, var3=None, var4=None):
        terminals = self.widgets['terminals']
        scroll = terminals.get_nth_page(terminals.get_current_page())
        vte = scroll.get_child()
        vte.copy_clipboard()
        return True

    def do_paste(self, widget, var2=None, var3=None, var4=None):
        terminals = self.widgets['terminals']
        scroll = terminals.get_nth_page(terminals.get_current_page())
        vte = scroll.get_child()
        vte.paste_clipboard()
        return True

    def do_search(self, widget):
        self.do_copy(widget)
        clipb = widget.get_clipboard(gtk.gdk.SELECTION_CLIPBOARD)
        text = clipb.wait_for_text()
        webbrowser.open_new_tab(constants.google_search_url % text)

    def do_set_title(self, widget):
        terminals = self.widgets['terminals']
        scroll = terminals.get_nth_page(terminals.get_current_page())
        vte = scroll.get_child()
        vte.copy_clipboard()
        clipb = widget.get_clipboard(gtk.gdk.SELECTION_CLIPBOARD)
        text = clipb.wait_for_text()
        if len(text) > 30:
            text = text[0:30]
        label = McmCheckbox(text)
        terminals.set_tab_label(scroll, label)
        self.set_window_title(text)

    def draw_column(self, tree, title, _id):
        tree.append_column(self.new_column(title, _id))

    def draw_consoles(self):
        terminals = self.widgets['terminals']
        pages = terminals.get_n_pages()
        conf = McmConfig()
        for i in range(pages):
            scroll = terminals.get_nth_page(i)
            term = scroll.get_child()
            color = gtk.gdk.color_parse(conf.get_bg_color())
            term.set_color_background(color)
            color = gtk.gdk.color_parse(conf.get_fg_color())
            term.set_color_foreground(color)
            opacity = (conf.get_bg_transparency() * 65535) / 100
            if conf.get_bg_transparent():
                term.set_background_image_file("")
                term.set_background_transparent(True)
                term.set_opacity(opacity)
                term.set_background_saturation(opacity * 0.00001)
            else:
                if len(conf.get_bg_image()) > 1:
                    term.set_background_image_file(conf.get_bg_image())
                    term.set_background_transparent(False)
                    term.set_opacity(100)
                    term.set_background_saturation(opacity * 0.00001)
                else:
                    term.set_background_transparent(False)
                    term.set_background_image_file("")

            term.set_font(conf.get_font())
            term.set_word_chars(conf.get_word_chars())
            term.set_scrollback_lines(conf.get_buffer_size())

    def draw_connection_widgets(self, alias):
        if alias == None:
            return
        connection = None
        try:
            connection = self.connections.get(alias)
        except KeyError:
            return
        label = self.widgets['cx_type']
        label.set_label("<b>%s</b>" % connection.get_type())
        label = self.widgets['alias_label']
        label.set_label("<b>%s</b>" % alias)
        self.draw_entry('user_entry', connection.user)
        self.draw_entry('host_entry', connection.host)
        self.draw_entry('port_entry', connection.port)
        self.draw_entry('password_entry', connection.password)
        self.draw_entry('options_entry', connection.options)
        self.draw_entry('description_entry', connection.description)

    def draw_entry(self, widget_name, text, tooltip_text=""):
        entry = self.widgets[widget_name]
        # entry_default_color = self.default_color
        # entry_default_state = gtk.STATE_NORMAL
        entry.set_text(text)
        entry.modify_base(gtk.STATE_NORMAL, self.default_color)
        entry.set_tooltip_text(tooltip_text)

    def draw_tree(self):
        tree = self.widgets['cx_tree']
        if len(tree.get_columns()) == 0:
            self.draw_column(tree, "Alias", 0)
        tree_store = gtk.TreeStore(str, str)
        tree.set_model(tree_store)

        groups = set()
        for cx in self.connections.get_all():
            groups.add(cx.group)

        for grp in groups:
            grp_node = tree_store.append(None, [grp, None])
            for cx in self.connections.get_all():
                if grp == cx.group:
                    tree_store.append(grp_node, [cx.alias, None])

    def edit_event(self, widget):
        alias = self.get_tree_selection()
        dlg = AddConnectionDialog(self.connections.get_aliases(), self.connections.get_groups(), types(), self.connections.get(alias))
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            cx = dlg.new_connection
            self.connections.add(cx.alias, cx)
            self.draw_tree()

    def entry_changed_event(self, widget):
        widget.modify_base(gtk.STATE_NORMAL, self.default_color)
        widget.set_tooltip_text(constants.press_enter_to_save)

    def events(self):
        events = {
            'on_main_mcm_destroy': self.quit_event,
            'on_connect_button_clicked': self.connect_event,
            'on_arrow_button_clicked': self.hide_unhide_tree,
            # Menu Items
            'on_mb_about_activate': self.about_event,
            'on_mb_help_activate': self.help_event,
            'on_mb_preferences_activate': self.preferences_event,
            'on_mb_save_activate': self.save_event,
            'on_mb_import_activate': self.import_csv_event,
            'on_mb_export_html_activate': self.export_html_event,
            'on_mb_export_csv_activate': self.export_csv_event,
            'on_mb_quit_activate': self.quit_event,
            'on_mb_add_activate': self.add_event,
            'on_mb_delete_activate': self.delete_event,
            'on_mb_connect_activate': self.connect_event,
            'on_mb_manage_activate': self.manage_event,
            'on_mb_cluster_toggled': self.hide_unhide_cluster_box,
            'on_mb_view_tree_toggled': self.hide_unhide_tree,
            'on_mb_tips_toggled': self.hide_unhide_tips,
            #'on_mb_update_tips_activate': self.update_tips,
            #'on_mb_http_server_activate': self.http_server,
            'on_mb_edit_activate': self.edit_event,
            # Status Icon Items
            'on_sib_quit_activate': self.quit_event,
            'on_sib_preferences_activate': self.preferences_event,
            'on_sib_add_activate': self.add_event,
            'on_sib_quit_activate': self.quit_event,
            'on_status_icon_menu_deactivate': self.on_status_icon_deactivate,
            'on_sib_home_activate': self.do_localhost,
            # Tree signals
            'on_connections_tree_row_activated': self.connect_event,
            'on_home_button_clicked': self.do_localhost,
            'on_connections_tree_cursor_changed': self.on_tree_item_clicked,
            'on_connections_tree_button_press_event': self.tree_submenu_event,
            # Entries Signales
            'on_user_entry_activate': self.update_connection,
            'on_user_entry_changed': self.entry_changed_event,
            'on_host_entry_activate': self.update_connection,
            'on_host_entry_changed': self.entry_changed_event,
            'on_port_entry_activate': self.update_connection,
            'on_port_entry_changed': self.entry_changed_event,
            'on_options_entry_activate': self.update_connection,
            'on_options_entry_changed': self.entry_changed_event,
            'on_description_entry_activate': self.update_connection,
            'on_description_entry_changed': self.entry_changed_event,
            'on_pwd_entry_activate': self.update_connection,
            'on_pwd_entry_changed': self.entry_changed_event,
            #Cluster Signals
            'on_cluster_entry_changed': self.cluster_event,
            'on_cluster_entry_activate': self.cluster_intro_event,
            'on_cluster_entry_backspace': self.cluster_backspace,
            # Notebook Signals
            #'on_terminals_change_current_page': self.switch_tab_event,
            #'on_terminals_select_page': self.switch_tab_event,
            'on_terminals_switch_page': self.switch_tab_event}
        return events

    def export_csv_event(self, widget):
        dlg = FileSelectDialog(FileSelectDialog.CSV)
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            _csv = ExportCsv(dlg.get_filename(), self.connections.get_all())
            idlg = UtilityDialogs()
            idlg.show_info_dialog(constants.export_csv, constants.saved_file % dlg.get_filename())

    def export_html_event(self, widget):
        dlg = FileSelectDialog(FileSelectDialog.HTML)
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            _html = Html(dlg.get_filename(), constants.version, self.connections.get_all())
            _html.export()
            idlg = UtilityDialogs()
            idlg.show_info_dialog(constants.export_html, constants.saved_file % dlg.get_filename())

    def f10_event(self, accel_group, window=None, keyval=None, modifier=None):
        return False

    def get_tree_selection(self, tree=None):
        '''Gets the alias of the connection currently selected on the tree'''
        if tree == None:
            tree = self.widgets['cx_tree']
        cursor = tree.get_selection()
        # model = tree.get_model()
        (model, i) = cursor.get_selected()
        if i == None:
            return None
        alias = model.get_value(i, 0)
        return alias
 
    def help_event(self, widget):
        webbrowser.open_new_tab(constants.mcm_help_url)

    def hide_unhide_cluster_box(self, widget):
        cl_box = self.widgets['cluster_entry']
        if widget.active:
            cl_box.show_all()
        else:
            cl_box.hide()

    def hide_unhide_tips(self, widget):
        tips_bar = self.widgets['tips_hbox']
        if widget.active:
            tips_bar.show_all()
        else:
            tips_bar.hide()

    def hide_unhide_tree(self, widget, window=None, key_val=None, modifier=None):
        # I have to define those parameters so the callbacks from the key bindings work
        vbox = self.widgets['vbox3']
        mb = self.widgets['mb_view_tree']
        if vbox.props.visible:
            mb.set_active(False)
            vbox.hide()
        else:
            mb.set_active(True)
            vbox.show_all()
        return True

    def import_csv_event(self, widget):
        dlg = FileSelectDialog(FileSelectDialog.CSV)
        dlg.run()
        cxs = None
        if dlg.response == gtk.RESPONSE_OK:
            _csv = Csv(dlg.uri)
            cxs = _csv.do_import()
            dlg = ImportProgressDialog(cxs, self.connections.get_aliases())
            dlg.run()
            print type(dlg.connections)
            self.connections.add_all(dlg.connections)
            self.draw_tree()

    def init_main_window(self):
        main_window = self.widgets['window']
        settings = gtk.settings_get_default()
        settings.props.gtk_menu_bar_accel = None
        self.keymap = gtk.gdk.keymap_get_default()
        accel_group = gtk.AccelGroup()
        main_window.add_accel_group(accel_group)
        self.widgets['accel_group'] = accel_group
        self.assign_key_binding(constants.hide_connections_keys, self.hide_unhide_tree)
        self.assign_key_binding(constants.terminal_home_keys, self.do_localhost)
        self.assign_key_binding('F10', self.f10_event)
        self.assign_key_binding(constants.tab_close_keys, self.close_tab_event)
        main_window.connect("delete-event", self.x_event)

        # Grab the default color
        try:
            self.default_color = DefaultColorSettings().base_color
        except AttributeError:
            self.default_color = gtk.gdk.color_parse('white')

        # Until I figure if I want this I'll disable it
        # mb_http_server = self.widgets['mb_http_server']
        # mb_http_server.hide()

        #Remove the first tab from the notebook
        self.terminals = self.widgets["terminals"]
        self.terminals.remove_page(0)

        main_window.show()
        self.hide_unhide_cluster_box(self.widgets['mb_cluster'])

    def init_status_icon(self, glade_home):
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_file(constants.icon_file)
        self.status_icon.set_tooltip(constants.app_name)
        self.status_icon.set_visible(True)
        self.status_icon.connect('activate', self.on_status_icon_activate)
        self.status_icon.connect('popup-menu', self.on_status_icon_popup)

    #def init_tips_menu(self):
        #tips_hbox = self.widgets["tips_hbox"]
        # Make this global so I can update the tips
        #self.tips_widget = McmTipsWidget(tips_hbox)

    def init_widgets(self):
        widgets = {
            'window': self.builder.get_object("main_mcm"),
            'about': self.builder.get_object("about_mcm"),
            'cx_tree': self.builder.get_object("connections_tree"),
            'cx_type': self.builder.get_object("combo_connection_type"),
            'user_entry': self.builder.get_object("user_entry"),
            'host_entry': self.builder.get_object("host_entry"),
            'port_entry': self.builder.get_object("port_entry"),
            'password_entry': self.builder.get_object("pwd_entry"),
            'options_entry': self.builder.get_object("options_entry"),
            'description_entry': self.builder.get_object("description_entry"),
            'alias_label': self.builder.get_object("alias_label"),
            'status_icon_menu': self.builder.get_object("status_icon_menu"),
            'connections_menu': self.builder.get_object("connections_menu"),
            'terminals': self.builder.get_object("terminals"),
            'hbox1': self.builder.get_object("hbox1"),
            'vbox3': self.builder.get_object("vbox3"),
            'vbox1': self.builder.get_object("vbox1"),
            'aspectframe1': self.builder.get_object("aspectframe1"),
            'cluster_entry': self.builder.get_object("cluster_entry"),
            'mb_cluster': self.builder.get_object("mb_cluster"),
            'mb_view_tree': self.builder.get_object("mb_view_tree"),
            'statusbar': self.builder.get_object("statusbar1"),
            'mb_http_server': self.builder.get_object("mb_http_server"),
            'menu2': self.builder.get_object("menu2"),
            # Tips Menu
            'tips_menubar': self.builder.get_object("tips_menubar"),
            'mi_tips': self.builder.get_object("mi_tips"),
            'tips_hbox': self.builder.get_object("tips_hbox"),
        }
        return widgets

    def manage_event(self, widget):
        dlg = ManageConnectionsDialog(self.connections, self.connections.get_groups(), types())
        dlg.run()
        if dlg.response is gtk.RESPONSE_OK:
            print "Saving"
            #self.dao.save_to_xml(dlg.connections.values())
            self.connections.save()
            self.draw_tree()
        dlg.destroy()

    def new_column(self, title, _id):
        column = gtk.TreeViewColumn(title, gtk.CellRendererText(), text=_id)
        column.set_resizable(True)
        column.set_sort_column_id(_id)
        return column

    def on_status_icon_activate(self, widget):
        main_window = self.widgets['window']
        if main_window.props.visible:
            main_window.hide()
        else:
            main_window.show()

    def on_status_icon_deactivate(self, widget):
        cx_menu = self.widgets['connections_menu']
        for i in cx_menu.get_children():
            cx_menu.remove(i)

    def on_tree_item_clicked(self, widget):
        self.draw_connection_widgets(self.get_tree_selection(widget))

    def on_status_icon_popup(self, status, button, time):
        cx_menu = self.widgets['connections_menu']
        for k in self.connections.keys():
            cx_item = gtk.MenuItem(k)
            cx_item.props.name = k
            cx_item.connect('activate', self.connect_event)
            cx_item.show()
            cx_menu.append(cx_item)

        s_i_menu = self.widgets['status_icon_menu']
        s_i_menu.popup(None, None, None, button, time)

    def preferences_event(self, widget):
        dlg = PreferencesDialog()
        dlg.run()
        if dlg.response == gtk.RESPONSE_OK:
            self.draw_consoles()

    def quit_event(self, widget, fck=None):
        dlg = UtilityDialogs()
        response = dlg.show_question_dialog(constants.quit_warning, constants.are_you_sure)
        if response == gtk.RESPONSE_OK:
            #self.dao.save_to_xml(self.connections.values())
            self.connections.save()
            exit(0)
        else:
            return False

    def rdp_connection(self, connection):
        """Embed a rdesktop window to our app"""
        terminals = self.widgets['terminals']
        label = gtk.Label(connection.alias)
        label.set_tooltip_text(connection.description)

        # menu_label = gtk.Label(connection.alias)

        socket = gtk.Socket()
        #index = terminals.append_page_menu(socket, label, menu_label)
        index = terminals.append_page(socket)
        sock_id = socket.get_id()
        cmd = ["rdesktop", "-K", "-X", str(sock_id), str(connection.host)]
        print cmd
        Popen(cmd)
        terminals.set_tab_reorderable(socket, True)
        self.assign_key_binding(constants.tabs_switch_keys % (index + 1), self.switch_tab)
        terminals.show_all()
        terminals.set_current_page(index)

    def save_event(self, widget):
        # self.dao.save_to_xml(self.connections.values())
        self.connections.save()

    def switch_tab(self, accel_group, window, keyval, modifier):
        # Key 0 is 48, Key 1 is 49 ... key 9 is 57
        index = keyval - 49
        terminals = self.widgets['terminals']
        terminals.set_current_page(index)
        self.switch_tab_event(terminals, None, index)
        return True # This will stop the vte from getting the annoying alt key

    def switch_tab_event(self, notebook, page, page_num):
        page = notebook.get_nth_page(page_num)
        label_title = notebook.get_tab_label(page).get_title()
        self.set_window_title(label_title)

    def set_window_title(self, title="MCM Connections Manager"):
        main_window = self.widgets['window']
        main_window.set_title(constants.window_title % title)

    def tab_close_button(self, title):
        button = gtk.Button(title, gtk.STOCK_CLOSE, False)
        return button

    def terminal_key_event(self, widget, event):
        if event.state & gtk.gdk.CONTROL_MASK:
            pgup = self.keymap.get_entries_for_keyval(gtk.keysyms.Page_Up)[0][0]
            pgdn = self.keymap.get_entries_for_keyval(gtk.keysyms.Page_Down)[0][0]
            if event.hardware_keycode is pgup:
                terminals = self.widgets['terminals']
                total = terminals.get_n_pages()
                page = terminals.get_current_page() + 1
                if page < total:
                    terminals.set_current_page(page)
                    self.switch_tab_event(terminals, None, page)
                return True
            elif event.hardware_keycode is pgdn:
                terminals = self.widgets['terminals']
                total = terminals.get_n_pages()
                page = terminals.get_current_page() - 1
                if page >= 0:
                    terminals.set_current_page(page)
                    self.switch_tab_event(terminals, None, page)
                return True
            else:
                return False
        else:
            return False

    def tree_submenu_event(self, widget, event):
        '''Draw a Menu ready to be inserted in tree'''
        if event.button == 1:
            return False
        elif event.button == 3:
            menu = self.widgets['menu2']
            menu.show_all()
            menu.popup(None, None, None, 3, event.time)
            return True
        else:
            return False

    def update_connection(self, widget):
        alias = self.get_tree_selection()
        connection = self.connections.get(alias)
        wid_name = widget.get_name()
        prop = widget.get_text()
        if wid_name == "user_entry":
            connection.user = prop
        elif wid_name == "host_entry":
            connection.host = prop
        elif wid_name == "port_entry":
            connection.port = prop
        elif wid_name == "options_entry":
            connection.options = prop
        elif wid_name == "description_entry":
            connection.description = prop
        elif wid_name == "pwd_entry":
            connection.password = prop
        self.connections.add(alias, connection)
        self.draw_connection_widgets(self.get_tree_selection())

    def update_tips(self, widget):
        response = self.tips_widget.update()
        dlg = UtilityDialogs()
        if not response:
            dlg.show_error_dialog(constants.update_tips_error_1, constants.update_tips_error_2)
        else:
            dlg.show_info_dialog(constants.update_tips_success_1, constants.update_tips_success_2 % response)

    def vnc_connect(self, connection):
        terminals = self.widgets['terminals']
        label = gtk.Label(connection.alias)
        label.set_tooltip_text(connection.description)
        menu_label = gtk.Label(connection.alias)
        vnc_client = MCMVncClient(connection.host, connection.port)
        vnc_box = vnc_client.get_instance()
        index = terminals.append_page_menu(vnc_box, label, menu_label)
        terminals.set_tab_reorderable(vnc_box, True)
        vnc_client.vnc.connect("vnc-disconnected", lambda term: self.vnc_disconnect(vnc_box, terminals))
        self.assign_key_binding(constants.tabs_switch_keys % (index + 1), self.switch_tab)
        terminals.show_all()
        terminals.set_current_page(index)

    def vnc_disconnect(self, box, terminals):
        index = terminals.get_current_page()
        terminals.remove_page(index)
        if terminals.get_n_pages() <= 0:
            terminals.hide()
        return True

    def x_event(self, x=None, y=None):
        self.quit_event(x)
        return True

if __name__ == '__main__':
    # Start the logging stuff
    # log_format = "%(asctime)s %(levelname)s: %(message)s"
    # logging.basicConfig(level=logging.INFO, format = log_format)

    mcmgtk = MCMGtk()
    gtk.main()
