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

def register_mcm_csv_dialect():
    import csv
    csv.register_dialect('mcm', delimiter=',', quoting=csv.QUOTE_ALL)

def import_csv(uri):
    import csv
    import mcm.common.connections
    import mcm.common.constants as constants
    
    connections = mcm.common.connections.ConnectionStore()
    connections.load()
    
    register_mcm_csv_dialect()
        
    existing_aliases = connections.get_aliases()
    with open(uri, 'rb') as csv_file:
        csvreader = csv.DictReader(csv_file, dialect='mcm')
        for row in csvreader:
            cx = mcm.common.connections.mapped_connections_factory(row)
            if cx:
                if cx.alias not in existing_aliases:
                    connections.add(cx.alias, cx)
                    print constants.import_not_saving % cx.alias
            else:
                print "Failed to import line %s" % csvreader.line_num
    connections.save()
    
def export_csv(connections, out_file_path=None):
    import csv, tempfile
    from  mcm.common.connections import fields
    
    if not out_file_path:
        out_file_path = tempfile.mkstemp()[1]
    
    register_mcm_csv_dialect()
    with open(out_file_path, 'wb') as ofile:
        writer = csv.DictWriter(ofile, fieldnames=fields, dialect='mcm')
        for cx in connections.get_all():
            writer.writerow(cx.to_dict())
    return out_file_path

def print_csv(connections):
    import sys, csv
    from  mcm.common.connections import fields
    register_mcm_csv_dialect()
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, dialect='mcm')
    for cx in connections.get_all():
        writer.writerow(cx.to_dict())

#    This encrypt/decrypt methods are from Eli Bendersky's website at:
#    http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
#    Thanks!

def encrypt_file(key, in_filename, out_filename, chunksize=64*1024):
    import random, struct
    from Crypto.Cipher import AES
    
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    import struct, tempfile
    import mcm.common.magic
    from Crypto.Cipher import AES
    
    if not out_filename:
        out_filename = tempfile.mkstemp()[1]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(origsize)
    
    # check the file type and return none if the file is data (should be csv)
    m = mcm.common.magic.Magic(mime=True)
    mime = m.from_file(out_filename)
    if mime == 'application/octet-stream':
        os.remove(out_filename)
        return None
    
    return out_filename