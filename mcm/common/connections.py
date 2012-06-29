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
import json
from mcm.common.configurations import McmConfig
from mcm.common.constants import connection_error, cxs_json

types = {'SSH':22, 'VNC':5900, 'RDP':3389, 'TELNET':23, 'FTP':21}

class Connection(object):

    def __init__(self, user, host, alias, password, port, group=None, \
                options=None, description=None):
        self.user = user
        self.host = host
        self.port = port
        self.group = group
        self.alias = alias
        self.password = password
        self.description = description
        self.options = options

    def cx_args(self, client, options, *args):
        """Creates a list containing all the arguments needed by subprocess"""
        _list = [self.command(client)]
        for option in options.split():
            _list.append(option)

        for arg in args:
            _list.append(arg)

        return _list

    def command(self, client):
        if os.path.exists(client) and os.access(client, os.X_OK):
            return client

    def print_connection(self, args):
        tstr = "Connecting: "
        for i in args:
            tstr += i + " "
        print tstr

    def get_type(self):
        return self.__class__.__name__.upper()

    def dialog_string(self):
        """Used to give a correct String for the dialog utility to show"""
        if self.get_type() == 'FTP':
            return "%s\tftp://%s@%s:%s\t\t %s" % (self.get_type(), self.user, \
                                    self.host, self.port, self.description)
        else:
            return "%s\t%s@%s:%s\t\t\t %s" % (self.get_type(), self.user, \
                                    self.host, self.port, self.description)

    def list_to_string(self, a_list):
        _str = " clear ; "
        for i in a_list:
            _str += " %s " % i
        return _str

    def to_dict(self):
        return {'user': self.user, 'host': self.host,
                'port': self.port, 'alias': self.alias,
                'password': self.password,
                'description': self.description, 'options': self.options,
                'group': self.group}

    def to_list(self):
        return [self.alias, self.get_type(), self.host, self.port,
        self.user, self.password, self.options, self.group, self.description]

    def get_html_tr(self):
        cxs = [self.alias, self.get_type(), self.host, self.port,
        self.user, self.options, self.group, self.description]
        tr = "<tr>"
        for cx in cxs:
            tr += "<td>%s</td>" % cx
        tr += "</tr>"
        return tr
    
    def __str__(self):
        return "%s %s %s@%s:%s" % (self.get_type(), self.alias,
        self.user, self.host, self.port)

class Ssh(Connection):
    
    def hostname(self):
        return "%s@%s" % (self.user, self.host)

    def scp_args(self, path):
        scp_path = "%s@%s:%s" % (self.user, self.host, path)
        return self.cx_args('scp', '', scp_path, '-p', self.port)

    def scp_cmd(self, path):
        a_list = self.scp_args()
        return self.list_to_string(a_list)

    def get_fork_args(self):
        conf = McmConfig()
        self.client, not_used = conf.get_ssh_conf()
        return [self.client, self.hostname(), "-p", self.port, self.options]

class Vnc(Connection):
    
    def vnchost(self):
        if self.port is not None and len(self.port) > 0:
            return "%s::%s" % (self.host, self.port)
        return self.host

    def get_fork_args(self):
        conf = McmConfig()
        self.client, options, embedded = conf.get_vnc_conf()
        return [self.client, self.options, self.vnchost()]

class Rdp(Connection):
    
    def rdphost(self):
        if self.port:
            return "%s:%s" % (self.host, self.port)
        return self.host

    def get_fork_args(self):
        conf = McmConfig()
        self.client, not_used = conf.get_rdp_conf()
        return [self.client, self.options, self.rdphost()]

class Telnet(Connection):
    
    def get_fork_args(self):
        conf = McmConfig()
        self.client, not_used = conf.get_telnet_conf()
        return [self.client, self.options, self.host, self.port]

class Ftp(Connection):
    
    def get_fork_args(self):
        conf = McmConfig()
        self.client, not_used = conf.get_ftp_conf()
        
        cmd = [self.client, '-u', self.user, '-p', self.port, self.host]
        if self.password:
            cmd[2] = '%s,%s' % (self.user,self.password)
        if self.options:
            cmd.insert(1,self.options)
        return cmd

def connections_factory(cx_type, cx_user, cx_host, cx_alias,
cx_password, cx_port, cx_group, cx_options, cx_desc):
    try:
        if not cx_alias:
            raise AttributeError("Bad format. Alias is not optional")

        cx = None
        if cx_type == 'SSH':
            cx = Ssh(cx_user, cx_host, cx_alias, cx_password,
                    cx_port, cx_group, cx_options, cx_desc)

        elif cx_type == 'VNC':
            cx = Vnc(cx_user, cx_host, cx_alias, cx_password,
                    cx_port, cx_group, cx_options, cx_desc)

        elif cx_type == 'RDP':
            cx = Rdp(cx_user, cx_host, cx_alias, cx_password,
                    cx_port, cx_group, cx_options, cx_desc)

        elif cx_type == 'TELNET':
            cx = Telnet(cx_user, cx_host, cx_alias, cx_password,
                        cx_port, cx_group, cx_options, cx_desc)

        elif cx_type == 'FTP':
            cx = Ftp(cx_user, cx_host, cx_alias, cx_password,
                    cx_port, cx_group, cx_options, cx_desc)

        else:
            raise AttributeError("Unknown Connection Type: %s" % cx_type)

        return cx

    except TypeError, err:
        print(err)
        exit(1)

class ConnectionStore(object):
    """
        Object to hold a map of alias:connections
    """
    def __init__(self):
        self.jsonfile = cxs_json
        self.store = {}
        
    def load(self):
        if not self.store:
            try:
                myfile = open(self.jsonfile, 'r')
                self.store = json.load(myfile, cls=ConnectionDecoder)
                myfile.close
            except IOError:
                print "Failed to load connections file"
            
        return self.store
    
    def save(self):
        myfile = open(self.jsonfile, 'w')
        json.dump(self.store, myfile, cls=ConnectionEncoder, encoding="utf-8", separators=(',',':'))
        myfile.close
        
    def save_to_file(self, filepath):
        try:
            myfile = open(filepath, 'w')
            json.dump(self.store, myfile, cls=ConnectionEncoder, encoding="utf-8", separators=(',',':'))
            myfile.close
        except IOError:
            print "Failed to save to file %s" % filepath
            
    def get_groups(self):
        groups = []
        for cx in self.store.values():
            if cx.group not in groups:
                groups.append(cx.group)
        return groups
    
    def get_aliases(self):
        return self.store.keys()
    
    def add(self, alias, cx):
        self.store[alias] = cx
        
    def update(self, alias, cx):
        self.store[alias] = cx
        
    def delete(self, alias):
        del self.store[alias]
        
    def get(self, alias):
        try:
            return self.store[alias]
        except KeyError:
            return None
        
    
    def get_all(self):
        return self.store.values()
    
    def add_all(self, connections):
        for alias, cx in connections.items():
            self.store[alias] = cx
        
class ConnectionEncoder(json.JSONEncoder):

    def default(self, clazz):
        if not isinstance(clazz, Connection):
            print connection_error
            return
        else:
            return dict(type=clazz.__class__.__name__.upper(),
                        user=clazz.user, host=clazz.host,
                        alias=clazz.alias, password=clazz.password,
                        port=clazz.port, group=clazz.group,
                        options=clazz.options, description=clazz.description)

class ConnectionDecoder(json.JSONDecoder):
    """
        Returns a List of Connections from a JSON String
    """

    def decode(self, json_str):
        cx_dict = json.loads(json_str)
        connections = {}
        for alias, cx in cx_dict.items():
            new_cx = connections_factory(cx['type'], 
                                         cx['user'],
                                         cx['host'],
                                         cx['alias'],
                                         cx['password'],
                                         cx['port'],
                                         cx['group'],
                                         cx['options'],
                                         cx['description'])
            connections[alias] = new_cx

        return connections
