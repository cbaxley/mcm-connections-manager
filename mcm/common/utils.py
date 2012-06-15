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
Some utility classes
'''

import os
import shutil
import csv
import json
import urllib
from StringIO import StringIO
from datetime import date
# from mcm.common.connections import *
import mcm.common.constants as constants

class Csv(object):
    def __init__(self, path):
        if os.path.exists(path) and os.access(path, os.W_OK):
            self.path = path
        else:
            raise IOError(constants.io_error % path)

    def do_import(self, pattern="alias"):
        """Returns a list with a dict"""
        cxs = []
        hdr = []
        csvreader = csv.reader(open(self.path, 'rb'))
        # From the header in the CSV we first get the header and create a list with it
        # then using this list, we iterate over the other rows creating a dict using
        # the header values as the keys and the row values for the dict values
        # then we save this dict to a list and return it.
        for row in csvreader:
            # Check if the row is the header
            if row[0] == pattern:
                for i in row:
                    hdr.append(i)
            else:
                cx = {}
                for i in range(len(hdr)):
                    _str = row[i]
                    cx[hdr[i]] = _str.strip()
                cxs.append(cx)
        return cxs

class Tip(object):
    """
    A tip belongs to a subsection, which belongs to a section.
    Each tip has a name or description and a value which is the
    command or whatever we want to use and an ID to help us
    find them.
    """

    def __init__(self, _id, section, subsection, name, value):
        self.id = _id # Not used for now
        self.section = section
        self.subsection = subsection
        self.name = name
        self.value = value

        # To make comparing faster
        self.uid = hash(name + value)

    def __str__(self):
        return "<Tip: %s @ %s:%s - %s: %s>" % (self.id, self.section, self.subsection, self.name, self.value)

    def __eq__(self, other):
        return self.uid == other.uid

    def __cmp__(self, other):
        return self.uid == other.uid

    def get_label(self):
        return "%s: %s" % (self.name, self.value)

    def get_breadcrumb_list(self):
        return [self.section, self.subsection, self.name]


class TipsEncoder(json.JSONEncoder):

    def default(self, clazz):
        if not isinstance(clazz, Tip):
            print constants.tip_error
            return
        else:
            return dict(section=clazz.section, subsection=clazz.subsection, name=clazz.name, value=clazz.value)


class TipsDecoder(json.JSONDecoder):
    """Returns a List of Tips from a JSON String"""

    def decode(self, json_str):
        tips_list = json.loads(json_str)
        tips = []
        i = 0
        for tip in tips_list:
            tip = Tip(i, tip['section'], tip['subsection'], tip['name'], tip['value'])
            tips.append(tip)
            i += 1

        return tips


class Tips(object):
    """
    An object to describe the Tips loaded from the JSON file.
    """

    def __init__(self):
        self.jsonfile = constants.tips_file
        self.list = None

    def read(self):
        """ Reads the tips file (JSON) and returns a List with all the Tip objects """
        if not self.list:
            myfile = open(self.jsonfile, 'r')
            self.list = json.load(myfile, cls=TipsDecoder)
            myfile.close
        return self.list

    def save(self, tips=None):
        """ Given a list of tips. Save them. If no list is provided, we use the one in the object. """
        if not tips:
            tips = self.list
        myfile = open(self.jsonfile, 'w')
        json.dump(tips, myfile, cls=TipsEncoder, encoding="utf-8", sort_keys=True, indent=4)
        myfile.close

    def dump(self, tips, filepath):
        """ Given a list of tips, save them to the specified file. Used to import from CSV """
        myfile = open(filepath, 'w')
        json.dump(tips, myfile, cls=TipsEncoder, encoding="utf-8", sort_keys=True, indent=4)
        myfile.close

    def update(self, filename=None):
        """Update the tips.json file, with the new tips from the given file or
        downloads the JSON file from Launchpad. The tips under the section 'MyTips'
        don't get updated or erased. A backup file is created.
        Returns a str with the update process we used. Or None if the update failed.
        """

        raw = None
        update_from = filename

        try:
            if not filename:
                sock = urllib.urlopen(constants.tips_url)
                raw = StringIO(sock.read())
                update_from = "web"
            else:
                raw = open(filename, 'r')

            # Backup the old file
            today = date.today()
            today = today.strftime("%d%m%y")
            shutil.copyfile(self.jsonfile, self.jsonfile + "_" + today + ".backup")

            my_tips_list = self.get_my_tips()
            new_tips_list = json.load(raw, cls=TipsDecoder)
            new_tips_list += my_tips_list
            unique_tips_list = list(set(new_tips_list)) # Eliminate Duplicates.

            self.list = unique_tips_list
            self.save()
            return update_from

        except IOError, e:
            print "Failed to Update"
            print e
            return None

    def get_my_tips(self):
        my_tips = []
        for tip in self.list:
            if tip.section == 'MyTips':
                my_tips.append(tip)
        return my_tips

    def get_max_id(self):
        return len(self.list)

    def get_subsections(self):
        subsections = []
        for tip in self.list:
            subsections.append(tip.subsection)
        return set(subsections)

    def get_sections(self):
        sections = []
        for tip in self.list:
            sections.append(tip.section)
        return set(sections)


# Use this script to create a json file from a CSV file
#if __name__ == '__main__':
#    _csv = Csv('/tmp/tips.csv')
#    rawtips = _csv.do_import("Section")
#
#    print constants.home
#
#    tips = []
#    for rawtip in rawtips:
#        tip = Tip(0, rawtip['Section'], rawtip['Subsection'], rawtip['Title'], rawtip['Value'])
#        tips.append(tip)
#
#    _tips = Tips()
#    _tips.dump(tips, "/tmp/tips.json")
#    tips_list = _tips.read()
#    tips_list += tips
#    unique_list = list(set(tips_list))
#    print unique_list

