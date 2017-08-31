from support import version

__author__ = version.get_author()
__version__ = version.get_version()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class Main(Gtk.Box):
    def __init__(self, text_edit):
        super(Main, self).__init__()
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.pack_start(self.listbox,True, True, 0)

        self.treerow = Gtk.ListBoxRow()
        self.rulesstore = RulesView(text_edit)
        self.tree = self.rulesstore.tree
        self.treerow.add(self.tree)
        self.listbox.add(self.treerow)
    def load_clientdb(self, clientdb):
        self.rulesstore.load_clientdb(clientdb)
        return -1
class RulesView(Gtk.TreeStore):
    def __init__(self, text_edit):
        Gtk.TreeStore.__init__(self, str, bool)
        self.connect('row-inserted', self.on_rowchange)
        self.__treesetup()
        self.connect('row-deleted', self.on_rowdelete)
        self.__last_change = list()
        self.__disable_rowchange = False
        self.__text_edit = text_edit
    def __treesetup(self):
        self.col = Gtk.TreeViewColumn("Listing")
        self.col_cell_text = Gtk.CellRendererText()

        self.col.pack_start(self.col_cell_text, True)
        self.col.add_attribute(self.col_cell_text, "text", 0)
        self.col.add_attribute(self.col_cell_text, "editable", 1)
        self.tree = Gtk.TreeView(self)
        self.tree.set_reorderable(True)
        self.tree.append_column(self.col)
        self.col_cell_text.connect('edited', self.__text_edited)
    def __treestoreload(self):
        self.clear()
        client_rules = self.__clientdb.get_rules_tup()
        for leadrule in client_rules:
            leader = self.append(None, [leadrule[0], leadrule[1]])
            for subrule in client_rules[leadrule]:
                self.append(leader, [subrule[0], subrule[1]])
    def load_clientdb(self, clientdb):
        self.__clientdb = clientdb
        self.__treestoreload()
        return -1
    def on_rowchange(self, tree_model, path, iter):
        if not self.__disable_rowchange:
            path_list = str(path).split(':')
            if path_list.__len__() >= 3:
                try:
                    self.__last_change.append(path)
                except:
                    self.__last_change = list()
                    self.__last_change.append(path)
    def iter_to_val(self, iter, idx):
        return self[iter][idx]
    def on_rowdelete(self, tree_model, path):
        if self.__last_change != list():
            self.__disable_rowchange = True
            over_parent = None
            tar_parent = None
            delete_rows = list()
            for tar_path in self.__last_change:
                try:
                    tar_iter = self.get_iter(tar_path)
                except:
                    tar_list = str(tar_path).split(':')
                    tar_iter = self.get_iter(self.__calc_path(tar_list))
                if self.iter_has_child(tar_iter):
                    over_parent = tar_iter
                else:
                    tar_parent = self.__top_parent(tar_iter)
                    self.__move_row(tar_iter, Gparent=tar_parent)
                    delete_rows.append(tar_iter)
            if over_parent != None:
                self.__move_row(over_parent,Gparent=tar_parent)
                delete_rows.append(over_parent)
            self.__last_change = list()
            for tar_iter in delete_rows:
                self.__del_row(tar_iter)
            self.__disable_rowchange = False
    def __top_parent(self, child):

        top_parent = self.iter_parent(self.iter_parent(child))
        top_top_parent = self.iter_parent(top_parent)
        if top_top_parent != None:
            top_parent = top_top_parent
        return top_parent
    def __calc_path(self, path_list):
        solved = False
        index = 0
        out_str = str()
        while not solved:
            if index <= path_list.__len__() - 1:
                out_str = str()
                new_val = str(int(path_list[index]) - 1)
                if int(new_val) < 0:
                    new_val = str(0)
                out_list = self.__copylist(path_list)
                del(out_list[index])
                out_list.insert(index, new_val)
                out_str = self.__com_pathlist(out_list)
                index += 1
                solved = self.__test_path(out_str)
        return out_str
    def __copylist(self, form_list):
        return list(form_list)
    def __com_pathlist(self, path_list):
        out_str = str()
        for idx, val in enumerate(path_list):
            if idx == 0:
                out_str += str(val)
            elif idx > 0:
                out_str += ':{}'.format(str(val))
        return out_str
    def __test_path(self, path):
        try:
            test_iter = self.get_iter(path)
            if self.get_value(test_iter, 0) != None:
                return True
            else:
                return False
        except:
            return False
    def __move_row(self, child, Gparent=None):
        if not Gparent:
            print('do things')
        else:
            mv = self.get_value(child, 0)
            mv_edit = self.get_value(child, 1)
            self.append(Gparent, [mv, mv_edit])
    def __del_row(self, child):
        self.remove(child)

    def __text_edited(self, widget, path, text):
        status = self.__text_edit(self[path][0], text)
        if status != -1:
            self[path][0] = text
    def convertstore(self):
        out_dict = dict()
        for treemodel in self:
            out_dict[treemodel[0]] = list()
            treemodel_child = treemodel.iterchildren()
            if treemodel_child != None:
                while True:
                    try:
                        treechild = treemodel_child.next()
                        out_dict[treemodel[0]].append(treechild[0])
                    except:
                        break
        return out_dict