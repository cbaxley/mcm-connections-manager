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
All the Export are handled from here
'''
import sys
from datetime import datetime


class Html(object):

    def __init__(self, mcm_version, connections):
        self.version = mcm_version
        self.connections = connections

    def export(self, out_file_path=None):
        
        if out_file_path:
            ofile = open(out_file_path, 'w')
            ofile.write(self.get_header())
            ofile.write(self.get_content())
            ofile.write(self.get_footer())
            ofile.close()
        else:
            sys.stdout.write(self.get_header())
            sys.stdout.write(self.get_content())
            sys.stdout.write(self.get_footer())

    def get_header(self):
        header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head><title>MCM Connections Manager Generated HTML \
Connections File</title>
<style type="text/css">
body{background-color:#b0c4de;}
#box-table-a
{
font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
font-size: 12px;
margin: 45px;
width: 90%;
text-align: left;
border-collapse: collapse;
}
#box-table-a th
{
font-size: 13px;
font-weight: normal;
padding: 8px;
background: #b9c9fe;
border-top: 4px solid #aabcfe;
border-bottom: 1px solid #fff;
color: #039;
}
#box-table-a td
{
padding: 8px;
background: #e8edff;
border-bottom: 1px solid #fff;
color: #669;
border-top: 1px solid transparent;
}
#box-table-a tr:hover td
{
background: #d0dafd;
color: #339;
}
</style>
</head>
<body>
<h2>MCM Connections Manager</h2>
        """
        return header

    def get_footer(self):
        gdate = datetime.today()
        return "<h3>Generated %s</h3></body></html>" % \
               gdate.strftime("%Y/%m/%d %H:%M:%S")

    def get_content(self):
        content = """
        <table id=\"box-table-a\"><thead><tr>
        <th scope=\"col\">Alias</th>
        <th scope=\"col\">Type</th>
        <th scope=\"col\">Host</th>
        <th scope=\"col\">Port</th>
        <th scope=\"col\">User</th>
        <th scope=\"col\">Options</th>
        <th scope=\"col\">Group</th>
        <th scope=\"col\">Description</th></tr></thead><tbody> """
        for cx in self.connections.get_all():
            content += cx.get_html_tr()
        content += "</tbody></table>"
        return content


class Odf(object):

    def __init__(self, out_file_path, mcm_version, connections):
        self.ofile = out_file_path
        self.version = mcm_version
        self.connections = connections

    def export(self):
        pass


def print_csv(connections, out_file_path=None):
    import csv
    csv.register_dialect('mcm', delimiter=',', quoting=csv.QUOTE_ALL)
    writer = None
    if out_file_path:
        with open(out_file_path, 'wb') as ofile:
            writer = csv.writer(ofile, dialect='mcm')
            writer.writerow(['alias', 'type', 'host', 'port', 'user',\
                        'password', 'options', 'group', 'description'])
            for cx in connections.get_all():
                writer.writerow(cx.to_list())
    else:
        writer = csv.writer(sys.stdout, dialect='mcm')
        writer.writerow(['alias', 'type', 'host', 'port', 'user',\
                        'password', 'options', 'group', 'description'])
        for cx in connections.get_all():
            writer.writerow(cx.to_list())
