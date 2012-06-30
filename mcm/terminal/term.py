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

'''
This is the main script for mcm
'''

import os, sys, subprocess, readline
from optparse import OptionParser

from tables import Table
from mcm.common.connections import types, connections_factory, Vnc, Rdp, ConnectionStore
from mcm.common.utils import Csv
import mcm.common.constants as constants


class Mcm(object):
    def __init__(self):
        self.dialog_binary = '/usr/bin/dialog'
        self.connections = ConnectionStore()
        self.connections.load()

    def do_connect(self, connection):
        connection.print_connection(connection.get_fork_args())
        try:
            subprocess.call(connection.get_fork_args())
        except (KeyboardInterrupt, SystemExit):
            exit(0)

    def connect(self, alias):
        try:
            conn = self.connections.get(alias)
            self.do_connect(conn)
        except KeyError:
            print "Error loading connections." 
            print "Please add one or more connections using \"mcm -a\""
            exit(1)

    def delete(self, alias):
        try:
            self.connections.delete(alias)
            print "Alias %s has been removed" % alias
            self.save_and_exit()
        except KeyError:
            print("Unknown alias " + alias)

    def export_html(self):
        from mcm.common.export import Html
        _html = Html(constants.version, self.connections) 
        _html.export()
        
    def export_csv(self):
        from mcm.common.export import print_csv
        print_csv(self.connections)

    def add(self, cxs=None):
        cx = None
        if cxs == None:
            print "Adding a new alias. Follow instructions"
            print "Type of server (%s) [default: SSH]:" % ", ".join(types)
            cx_type = raw_input()
            cx_type = cx_type.upper()
            if len(cx_type) <= 0:
                cx_type = 'SSH'

            if cx_type not in types:
                    raise TypeError("Unknown server type: " + cx_type)

            print "Alias for this connection:"
            cx_alias = raw_input()
            if self.connections != None:
                if self.connections.get(cx_alias) != None:
                    raise TypeError("This alias is already used. Try with another one")

            print "Hostname or IP Address:"
            cx_host = raw_input()
            if len(cx_host) <= 0:
                raise TypeError("Provide a hostname or IP address")

            print "Username:"
            cx_user = raw_input()

            print "Password:"
            cx_password = raw_input()

            print "Port [default: ] : "
            raw_cx_port = raw_input()
            cx_port = int(raw_cx_port)

            print "Group (%s):" % ", ".join(self.connections.get_groups())
            cx_group = raw_input()
            if len(cx_group) <= 0:
                raise TypeError("Provide a the name of an existing group or a new one")

            print "Options:"
            cx_options = raw_input()

            print "Description:"
            cx_desc = raw_input()

            cx = connections_factory(cx_type, cx_user, cx_host, cx_alias, cx_password, cx_port, cx_group, cx_options, cx_desc)
            self.connections.add(cx_alias, cx)
            print "saved %s" % cx

        else:
            for d in cxs: # d is a dict
                alias = d['alias'].strip()
                if len(d) != 10:
                    raise TypeError("Not a parseable Connection List")
                if self.connections.get(alias):
                    print "Not saving %s" % alias
                    continue
                cx = connections_factory(d['type'], d['user'], d['host'], alias, d['password'], d['port'], d['group'], d['options'], d['description'])
                self.connections.add(alias, cx)
                print "saved %s" % cx
                
        self.save_and_exit()

    def show_connection(self, alias):
        t_headers = ['Alias', 'user', 'host', 'port']
        t_rows = []
        if alias:
            conn = self.connections.get(alias)
            if conn:
                t_rows.append((conn.alias, conn.user, conn.host, conn.port))
                
        table = Table(t_headers, t_rows)
        table.output()
        exit(0)


    def list_connections(self):
        print "Usage: mcm [OPTIONS] [ALIAS]\n"
        t_headers = ['Aliases', 'Type', 'user', 'host', 'port']
        t_rows = []
        keys = self.connections.get_aliases()
        keys.sort()
        for key in keys:
            conn = self.connections.get(key)
            if type(conn) is not Vnc and type(conn) is not Rdp:
                t_rows.append((conn.alias, conn.get_type(), conn.user, conn.host, conn.port))

        table = Table(t_headers, t_rows)
        table.output()
        print "=" * 80

    def show_menu(self):
        if os.path.exists(self.dialog_binary):
            alias = self.show_menu_dialog()
            self.connect(alias)
        else:
            self.list_connections()
            readline.set_completer(self.completer)
            readline.parse_and_bind("tab: complete")
            
            try:
                alias = raw_input("mcm: ")
                if alias and self.connections.get(alias):
                    self.connect(alias)
                else:
                    print "Unknown alias %s" % alias
            except (KeyboardInterrupt, EOFError):
                exit(0)
            
    def completer(self, text, state):
        options = [x for x in self.connections.get_aliases() if x.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None

        
    def show_menu_dialog(self):
        '''Show a dialog, catch its output and return it for do_connect'''
        menu_size = 20
        if len(self.connections.store) < menu_size:
            menu_size = str(len(self.connections.store))
        else:
            menu_size = str(menu_size)
        dialog = [
                self.dialog_binary, 
                '--backtitle', 'mcm ' + constants.version, 
                '--clear', '--menu', 
                '"Choose an Alias to connect to"', 
                '0', '150', menu_size
                ]
        keys = self.connections.get_aliases()
        keys.sort()
        for key in keys:
            conn = self.connections.get(key)
            dialog.append(key)
            dialog.append(conn.dialog_string())
        fhandlr = open('/tmp/mcm_ans', 'w+')
        try:
            #print dialog
            res = subprocess.call(dialog, stderr=fhandlr)
            if res == 1:
                raise SystemExit()
        except (KeyboardInterrupt, SystemExit):
            sys.exit(0)

        fhandlr.seek(0)
        aliases = fhandlr.readlines()
        fhandlr.close()
        return aliases[0]

    def save_and_exit(self):
        self.connections.save()
        exit(0)

    def import_csv(self, path):
        _csv = Csv(path)
        cxs = _csv.do_import()
        print cxs
        self.add(cxs)

if __name__ == '__main__':
    
    usage = """%prog [OPTIONS] [ALIAS]
With no options, prints the list of connections
example:
%prog foo\t\tConnects to server foo
    """
    
    parser = OptionParser(usage="", version=constants.version)
    parser.add_option("-a", "--add", action="store_true", dest="add", help="Add a new connection")
    parser.add_option("-l", "--list", action="store_true", dest="list", help="Complete list of connections with all data")
    parser.add_option("-s", "--show", action="store", dest="show", help="Delete the given connection alias")
    parser.add_option("-d", "--delete", action="store", dest="delete_alias", help="Show the given connection alias")
    parser.add_option("--export-html", action="store_true", dest="export_html", 
                      help="Print the connections in HTML format")
    parser.add_option("--export-csv", action="store_true", dest="export_csv", 
                      help="Print the connections in CSV format")
    parser.add_option("--import-csv", action="store", dest="import_csv",
                      help="Import the connections from the given CSV file")

    (options, args) = parser.parse_args()

    mcmt = Mcm()

    if not options.list \
        and not options.add \
        and not options.show \
        and not options.delete_alias \
        and not options.export_html \
        and not options.export_csv \
        and not options.import_csv \
        and len(args) < 1:
            mcmt.show_menu()

    # I want only one option at a time
    if options.add \
        and (options.list 
             or options.show 
             or options.export_html 
             or options.export_csv 
             or options.import_csv):
        parser.error("Only one option at a time")

    if options.list and options.show and options.export_html and options.export_csv and options.import_csv:
        parser.error("Only one option at a time")

    if options.add:
        try:
            mcmt.add()
        except (KeyboardInterrupt, TypeError, ValueError) as e:
            if type(e) is not KeyboardInterrupt:
                print e
                exit(1)

    if options.list:
        mcmt.list_connections()
        
    if options.show:
        mcmt.show_connection(options.show)

    if options.delete_alias:
        mcmt.delete(options.delete_alias)

    if options.export_html:
        mcmt.export_html()

    if options.export_csv:
        mcmt.export_csv()
        
    if options.import_csv:
        mcmt.import_csv(options.import_csv)

    if len(args) > 0:
        mcmt.connect(options.show)
        


