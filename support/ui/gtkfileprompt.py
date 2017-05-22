from support import version

__author__ = version.get_author()
__version__ = version.get_version()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

class NewClientDialog(Gtk.Dialog):

    def __init__(self, parent, last_selection=None):
        Gtk.Dialog.__init__(self, "Create New Client", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(1, 1)
        self.name_grid = Gtk.Grid()
        self.namefirst = Gtk.Entry()
        self.namefirst.set_placeholder_text('First')
        self.namelast = Gtk.Entry()
        self.namelast.set_placeholder_text('Last')
        self.name_grid.attach(self.namefirst, 0,0,1,1)
        self.name_grid.attach(self.namelast, 1,0,1,1)
        self.name_grid.set_border_width(10)
        self.name_grid.set_column_spacing(10)
        name_frame = Gtk.Frame()
        name_frame.set_border_width(10)
        box = self.get_content_area()
        box.add(name_frame)
        name_frame.set_label("Client Name")
        name_frame.add(self.name_grid)
        self.show_all()


class FileChooser(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self, parent=parent)
        self.show_all()
class FileChooserOpenDB(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self, parent=parent, action=Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        self.set_title('Open ClientDB')
        filter = Gtk.FileFilter()
        filter.set_name('ClientDB')
        filter.add_mime_type("application/x-sqlite3")
        filter.add_pattern("*.db")
        self.add_filter(filter)
class FileChooserOpenCSV(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.FileChooserDialog.__init__(self, parent=parent, action=Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        self.set_title('Import .csv files')
        filter = Gtk.FileFilter()
        filter.set_name('.csv')
        filter.add_mime_type("text/csv")
        filter.add_pattern("*.csv")
        self.set_select_multiple(True)
        self.add_filter(filter)
class FileChooserSaveDB(Gtk.FileChooserDialog):
    def __init__(self, parent, reccomended_name=None):
        Gtk.FileChooserDialog.__init__(self, parent=parent, action=Gtk.FileChooserAction.SAVE, buttons=(Gtk.STOCK_SAVE_AS, Gtk.ResponseType.OK))
        self.set_title('Save ClientDB')
        filter = Gtk.FileFilter()
        filter.set_name('ClientDB')
        filter.add_mime_type("application/x-sqlite3")
        filter.add_pattern("*.db")
        self.add_filter(filter)
        if reccomended_name != None:
            self.set_current_name(convert_rec(reccomended_name))
class FileChooserSaveEXCEL(Gtk.FileChooserDialog):
    def __init__(self, parent, reccomended_name=None):
        Gtk.FileChooserDialog.__init__(self, parent=parent, action=Gtk.FileChooserAction.SAVE, buttons=(Gtk.STOCK_SAVE_AS, Gtk.ResponseType.OK))
        self.set_title('Save Report As')
        filter = Gtk.FileFilter()
        filter.set_name('Excel')
        filter.add_mime_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        filter.add_pattern("*.xlsx")
        self.add_filter(filter)
        if reccomended_name != None:
            self.set_current_name(reccomended_name)
def convert_rec(name):
    return '{}-{}.db'.format(name[1], name[0])