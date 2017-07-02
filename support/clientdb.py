from support import version
__author__ = version.get_version()
__version__ = version.get_author()

import sqlite3, hashlib, os
from support import parser, exelgen
from random import randint

class MainFile():

    def __init__(self, file_name):
        self.__conn = sqlite3.connect(file_name)
        self.__c = self.__conn.cursor()

    def get_clientname(self):
        try:
            client_name = str()
            for client_data in self.__c.execute('SELECT * FROM userinfo'):
                client_name = client_data
            if client_name == str():
                return -1
            else:
                return client_name
        except sqlite3.OperationalError:
            return -1

    def set_clientname(self, namefirst, namelast):
        cur_name = self.get_clientname()
        if cur_name != -1:
            print('hell11o')
        else:
            try:
                self.__c.execute('''CREATE TABLE userinfo
            (first name, last name)''')
                self.__c.execute("INSERT INTO userinfo VALUES ('{}', '{}')".format(namefirst, namelast))
            except sqlite3.OperationalError:
                self.__c.execute("INSERT INTO userinfo VALUES ('{}', '{}')".format(namefirst, namelast))
        return 1
    def iterate_listing(self, listing_id):
        for row in self.__c.execute("SELECT * FROM entries"):
            if row[0] == listing_id:
                yield row
    def iterate_sort(self):
        rules = self.get_rules()
        out_dict = dict()
        for parentlisting in rules:
            out_dict[parentlisting] = list()
            for entry in self.iterate_listing(parentlisting):
                out_dict[parentlisting].append(entry)
            for sublisting in rules[parentlisting]:
                for entry in self.iterate_listing(sublisting):
                    out_dict[parentlisting].append(entry)
        return out_dict
    def __pack_format(self, entry):
        pack_format = {0:{'date':entry[1],'start_date':entry[2],'guest':entry[5],'earning':entry[4],'stay':entry[3],'clean_fee':entry[7],'type':entry[6]},1:{'start_date':entry[2],'stay':entry[3],'guest':entry[5],'type':entry[6]},2:{'date':entry[1],'guest':entry[5],'earning':entry[4], 'type':entry[6]}}
        return pack_format[entry[6]]
    def pack(self):
        sorted_pack = self.iterate_sort()
        out_dict = dict()
        for lead_id in sorted_pack:
            lead_listing = self.id_to_listing(lead_id)
            out_dict[lead_listing] = list()
            for entry in sorted_pack[lead_id]:
                out_dict[lead_listing].append(self.__pack_format(entry))
        return out_dict
    def append_csv(self, report):
        with open(report, encoding='utf-8') as rawreport:
            reportparse = parser.report(rawreport)
        if reportparse.type() != -1:
            with open(report, 'rb') as rawreport:
                filehash = md5(rawreport)
            hashmatch = False
            hashlist = list()
            for hashdata in self.__c.execute("SELECT * FROM files"):
                hashlist.append(hashdata)
                if hashdata[0] == filehash:
                    hashmatch = True
            if not hashmatch:
                listing_command = "INSERT INTO entries VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                randomg = randgen()
                hashmatch = True
                hashid = randomg.threegen()
                while hashmatch:
                    hashid = randomg.threegen()
                    count_match = 0
                    for hashdata in hashlist:
                        if hashid == hashdata[1]:
                            count_match += 1
                    if count_match == 0:
                        hashmatch = False
                self.__c.execute("INSERT INTO files VALUES ('{}','{}')".format(filehash,hashid))
                csv_type = reportparse.type()
                nil = ''
                for listing in reportparse.pack():
                    listing_id = self.append_listing(listing)
                    for entry in reportparse.pack()[listing]:
                        if csv_type == 0:
                            self.__c.execute(listing_command.format(listing_id, entry['date'],entry['start_date'],entry['stay'],entry['earning'],entry['guest'], csv_type, entry['clean_fee']))
                        elif csv_type == 1:
                            self.__c.execute(
                                listing_command.format(listing_id,
                                                                                                               nil,
                                                                                                               entry['start_date'],
                                                                                                               entry['stay'],
                                                                                                               nil,
                                                                                                               entry['guest'],
                                                                                                               csv_type,
                                                                                                                nil))
                        elif csv_type == 2:
                            self.__c.execute(
                               listing_command.format(listing_id,
                                                                                                               entry['date'],
                                                                                                               nil,
                                                                                                               nil,
                                                                                                               entry['earning'],
                                                                                                               entry['guest'],
                                                                                                               csv_type,
                                                                                                               nil))
    def get_listings(self):
        return -1
    def append_listing_override(self, listing_tup, ignore=False):
        found = self.get_listing_present(listing_tup[2])
        if not found or ignore:
            self.__c.execute("INSERT INTO listings VALUES ('{}', '{}', '{}', {})".format(listing_tup[0], listing_tup[1], listing_tup[2], listing_tup[3]))
            return 1
        elif found and not ignore: return -1
    def append_listing(self, addlisting, parent='top', edit=False):
        listings = list()
        listing_edit = {False:0,True:1}
        found = False
        id = int()
        for listing in self.__c.execute('SELECT * FROM listings'):
            listings.append(listing)
            if listing[2] == addlisting:
                found = True
                id = listing[0]
        if found:
            return id
        else:
            numgen = randgen()
            match = True
            while match:
                id = numgen.generate()
                count_match = 0
                for listing in listings:
                    if id == listing[0]:
                        count_match += 1
                if count_match == 0:
                    match = False
            self.__c.execute("INSERT INTO listings VALUES ('{}', '{}', '{}', {})".format(id, parent, addlisting, listing_edit[edit]))
            return id
    def id_to_listing(self, id, idx=2):
        out_listing = str()
        for row in self.__c.execute("SELECT * FROM listings"):
            if row[0] == id:
                out_listing = row[idx]
        return out_listing
    def listing_to_id(self, listing, idx=0):
        out_id = str()
        for row in self.iter_listing():
            if row[2] == listing:
                out_id = row[idx]
        return out_id
    def get_name(self):
        out_name = None
        for entry in self.__c.execute("SELECT * FROM userinfo"):
            out_name = entry
        return out_name
    def get_full_name(self):
        name = self.get_name()
        return '{} {}'.format(name[0],name[1])
    def get_rules(self, index=0):
        rules = dict()
        listings = list()
        for listing in self.__c.execute("SELECT * FROM listings"):
            if listing[1] == 'top':
                rules[listing[index]] = list()
            else:
                listings.append(listing)
        for listing in listings:
            if index == 0:
                rules[listing[1]].append(listing[0])
            else:
                rules[self.id_to_listing(listing[1])].append(listing[2])
        return rules
    def iter_listing(self):
        for listing in self.__c.execute("SELECT * FROM listings"):
            yield listing
    def get_listing_val(self, value, idxmatch, idxfind):
        out_val = None
        for listing in self.iter_listing():
            if value == listing[idxmatch]:
                out_val = listing[idxfind]
        return out_val
    def remove_listing(self, listing, ignore=False):
        editable = self.get_listing_val(listing, 2,3)
        if editable == 1 or ignore:
            self.__c.execute("DELETE FROM listings WHERE listing='{}'".format(listing))
        elif editable == 0 and not ignore:
            return -1
    def get_listing_present(self, listing, idx=2):
        present = False
        for listing_check in self.iter_listing():
            if listing_check[idx] == listing: present=True
        return present
    def get_listing_data(self, listing, idx=2):
        listing_data = None
        for row in self.iter_listing():
            if row[idx] == listing: listing_data = row
        return listing_data
    def rename_listing(self, listing, new_name):
        editable = self.get_listing_val(listing, 2, 3)
        present = self.get_listing_present(new_name)
        if editable == 1 and not present:
            listing_data = self.get_listing_data(listing)
            self.remove_listing(listing)
            listing_append = (listing_data[0],listing_data[1],new_name,1)
            self.append_listing_override(listing_append)
            return 1
        elif editable == 0 or present:
            return -1
    def set_listing_parent(self, listing_id, parent_id):
        listing_data = self.get_listing_data(listing_id, idx=0)
        new_tup = (listing_data[0], parent_id, listing_data[2],listing_data[3])
        self.remove_listing(listing_data[2], ignore=True)
        self.append_listing_override(new_tup, ignore=True)
    def get_rules_tup(self):
        rules = dict()
        listings = list()
        for listing in self.__c.execute("SELECT * FROM listings"):
            if listing[1] == 'top':
                listing_tup = (listing[2],listing[3])
                rules[listing_tup] = list()
            else:
                listings.append(listing)
        for listing in listings:
            head_listing_tup = (self.id_to_listing(listing[1]), self.id_to_listing(listing[1],idx=3))
            sub_listing_tup = (listing[2], listing[3])
            rules[head_listing_tup].append(sub_listing_tup)
        return rules
    def set_rules(self, rules):
        for lead_listing in rules:
            lead_id = self.listing_to_id(lead_listing)
            self.set_listing_parent(lead_id, 'top')
            for sub_lisiting in rules[lead_listing]:
                sub_id = self.listing_to_id(sub_lisiting)
                self.set_listing_parent(sub_id, lead_id)
        return 1
    def save(self):
        self.__conn.commit()
    def close(self):
        self.__conn.close()

class randgen():
    def __init__(self):
        self.__alph = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',1,2,3,4,5,6,7,8,9]
        self.__alphlen = self.__alph.__len__() - 1
    def generate(self):
        int1 = randint(0, self.__alphlen)
        int2 = randint(0, self.__alphlen)
        return '{}{}'.format(self.__alph[int1], self.__alph[int2])
    def threegen(self):
        int1 = randint(0, self.__alphlen)
        int2 = randint(0, self.__alphlen)
        int3 = randint(0, self.__alphlen)
        return '{}{}{}'.format(self.__alph[int1], self.__alph[int2], self.__alph[int3])

def md5(raw_file):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: raw_file.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

def createdb(file_name, firstname, lastname):
    conn = sqlite3.connect(file_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE userinfo
    ('first name' name, 'last name' name)''')
    c.execute('''CREATE TABLE listings
    ('listing id' id, 'parent id' id, 'listing' TEXT, 'edit' BIT)''')
    c.execute('''CREATE TABLE entries
    ('listing id' id, 'payment date' date, 'arrival date' date, 'stay duration' bigint, 'amount' money, 'guest' name, 'service' int, 'cleaning fee' money)''')
    c.execute('''CREATE TABLE files
    (md5, id)''')
    conn.commit()
    conn.close()
    new_file = MainFile(file_name)
    new_file.set_clientname(firstname, lastname)
    new_file.save()
    return new_file


if __name__ == '__main__':
    test_file = createdb('empty.db', 'April', 'Dace')