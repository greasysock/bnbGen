from support import version

__author__ = version.get_author()
__version__ = version.get_version()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from support.ui import gtkfileprompt
from support import clientdb

class bar(Gtk.MenuBar):
    def __init__(self, about, top_parent):
        self.__top_parent = top_parent
        Gtk.MenuBar.__init__(self)
        file_menu = Gtk.Menu()
        tools_menu = Gtk.Menu()
        help_menu = Gtk.Menu()

        file_menu_dropdown = Gtk.MenuItem('File')
        tools_menu_dropdown = Gtk.MenuItem('Tools')
        help_menu_dropdown = Gtk.MenuItem('Help')

        file_new = Gtk.MenuItem("New")
        file_open = Gtk.MenuItem("Open")
        file_save = Gtk.MenuItem("Save")
        file_saveas = Gtk.MenuItem("Save As...")
        file_exit = Gtk.MenuItem("Exit")

        tools_import = Gtk.MenuItem('Import...')

        help_about = Gtk.MenuItem("About")

        file_menu_dropdown.set_submenu(file_menu)
        tools_menu_dropdown.set_submenu(tools_menu)
        help_menu_dropdown.set_submenu(help_menu)

        file_menu.append(file_new)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(file_open)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(file_save)
        file_menu.append(file_saveas)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(file_exit)

        tools_menu.append(tools_import)

        help_menu.append(help_about)

        self.__about = about
        self.append(file_menu_dropdown)
        self.append(tools_menu_dropdown)
        self.append(help_menu_dropdown)
        help_about.connect("activate", self.about_selected)
        file_new.connect("activate", self.new_selected)
        file_open.connect("activate", self.open_selected)
        file_exit.connect("activate", Gtk.main_quit)
        tools_import.connect("activate", self.tools_import_selected)
        file_save.connect("activate", self.file_save_selected)

    def about_selected(self, arg):
        self.__about.showabout()
    def new_selected(self, arg):
        new_client = gtkfileprompt.NewClientDialog(self.__top_parent)
        response = new_client.run()
        if response == Gtk.ResponseType.OK:
            name = (new_client.namefirst.get_text(),new_client.namelast.get_text())
            name_test = self.__name_test(name)
            if name_test:
                savedialog = gtkfileprompt.FileChooserSaveDB(self.__top_parent, reccomended_name=name)
                save_response = savedialog.run()
                if save_response == Gtk.ResponseType.OK:
                    file = savedialog.get_filename()
                    clientdb.createdb(file, name[0], name[1])
                    self.__top_parent.open_client(file)
                savedialog.destroy()
        new_client.destroy()
    def file_save_selected(self, arg):
        if self.__top_parent.clientdbload != None:
            rules = self.__top_parent.clientpane.rulesstore.convertstore()
            self.__top_parent.clientdbload.set_rules(rules)
            self.__top_parent.clientdbload.save()
    def open_selected(self, arg):
        opendialog = gtkfileprompt.FileChooserOpenDB(self.__top_parent)
        response = opendialog.run()
        if response == Gtk.ResponseType.OK:
            self.__top_parent.open_client(opendialog.get_filename())
        opendialog.destroy()
    def tools_import_selected(self, arg):
        if self.__top_parent.clientdbload != None:
            opendialog = gtkfileprompt.FileChooserOpenCSV(self.__top_parent)
            response = opendialog.run()
            if response == Gtk.ResponseType.OK:
                for file in opendialog.get_filenames():
                    filetype = type(file)
                    if filetype == str:
                        self.__top_parent.clientdbload.append_csv(file)
                self.__top_parent.refresh_clientdb()
            opendialog.destroy()
    def __name_test(self, name):
        return True