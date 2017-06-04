#!/usr/bin/python3
from support import version
__author__ = version.get_author()
__version__ = version.get_version()

__title__ = 'bnbGen'
__website__ = 'www.bnbwithme.com'
__about_logo__ = 'support/ui/logo.png'
__logo__ = 'support/ui/logo.png'
__description__ = 'Designed for bnbwithme as a monthly reports generator. \'{}\' takes .csv files provided by airbnb and VRBO and creates a correctly formatted excel file.'.format(__title__)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from support import clientdb, exelgen, filegen
from support.ui import ClientPane, MenuBar, gtkfileprompt

class NewListingDialog(Gtk.Dialog):

    def __init__(self, parent, last_selection=None):
        Gtk.Dialog.__init__(self, "New", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(1, 1)
        self.name_grid = Gtk.Grid()
        self.namefirst = Gtk.Entry()
        self.namefirst.set_placeholder_text('Title')
        self.name_grid.attach(self.namefirst, 0,0,1,1)
        self.name_grid.set_border_width(10)
        self.name_grid.set_column_spacing(10)
        name_frame = Gtk.Frame()
        name_frame.set_border_width(10)
        box = self.get_content_area()
        box.add(name_frame)
        name_frame.set_label("Listing Title")
        name_frame.add(self.name_grid)
        self.show_all()
class ToolBar(Gtk.Toolbar):
    def __init__(self, signal_gen, add_press_signal, remove_press_signal):
        Gtk.Toolbar.__init__(self)
        export = Gtk.ToolButton(Gtk.STOCK_EXECUTE)
        export.set_tooltip_text('Run Report...')
        new_title = Gtk.ToolButton(Gtk.STOCK_ADD)
        new_title.set_tooltip_text('Add listing title...')
        remove_title = Gtk.ToolButton(Gtk.STOCK_REMOVE)
        remove_title.set_tooltip_text('Remove listing title...')
        self.insert(export, 0)
        self.insert(new_title, 1)
        self.insert(remove_title, 2)

        export.connect("clicked", self.connectpress)
        new_title.connect("clicked", self.addpress)
        remove_title.connect("clicked", self.rempress)
        self.__report_signal = signal_gen
        self.__add_signal = add_press_signal
        self.__rem_signal = remove_press_signal
    def connectpress(self, gpointed):
        self.__report_signal()
    def addpress(self, arg):
        dialog = self.__add_signal()
    def rempress(self, arg):
        self.__rem_signal()
class MonthStore(Gtk.ListStore):
    def __init__(self):
        Gtk.ListStore.__init__(self, str)
        self.MonthCombo = Gtk.ComboBoxText()
        self.MonthCombo.set_entry_text_column(0)
        self.months = ["Janurary", "Feburary", "March", "April", "May", "June", "July", "August", "September", "October",
                  "November", "December"]
        for month in self.months:
            self.MonthCombo.append_text(month)

class MonthDialog(Gtk.Dialog):

    def __init__(self, parent, last_selection=None):
        Gtk.Dialog.__init__(self, "Month Selection", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        monthstore = MonthStore()
        self.monthcombo = monthstore.MonthCombo
        if last_selection != None:
            self.monthcombo.set_active(last_selection)
        frame = Gtk.Frame()
        frame.set_border_width(10)
        box = self.get_content_area()
        box.add(frame)
        frame.set_label("Month")
        frame.add(self.monthcombo)
        self.show_all()
    def getselection(self):
        return self.monthcombo.get_active() + 1
class AboutDialog(Gtk.AboutDialog):
    def __init__(self):
        Gtk.AboutDialog.__init__(self)
        self.set_program_name(__title__)
        self.set_version('v{}'.format(__version__))
        self.set_authors([__author__])
        self.set_website(__website__)
        self.set_comments(__description__)
        aboutlogo = GdkPixbuf.Pixbuf.new_from_file(__about_logo__)

        self.set_logo(aboutlogo)
        self.connect("response", self.hideabout)
        self.connect("delete-event", self.hideabout)
    def showabout(self):
        self.show_all()
    def hideabout(self, response, arg):
        self.hide()
class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="{}".format(__title__))
        logo = GdkPixbuf.Pixbuf.new_from_file(__logo__)
        self.set_icon(logo)
        self.set_default_size(1280,720)

        self.about = AboutDialog()
        self.about.set_transient_for(self)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.menubar = MenuBar.bar(self.about, self)
        self.toolbar = ToolBar(self.report_gen, self.add_listing, self.remove_listing)
        self.clientpane = ClientPane.Main(self.text_edit)
        self.box.pack_start(self.menubar, False, False, 0)

        self.box.pack_start(self.clientpane, False, False, 0)
        self.box.pack_end(self.toolbar, False, False, 0)

        self.add(self.box)
        self.clientdbload = None
    def open_client(self, client_db):
        self.clientdbload = clientdb.MainFile(client_db)
        self.set_title('{} - {}'.format(self.clientdbload.get_full_name(),__title__))
        self.clientpane.load_clientdb(self.clientdbload)
        return -1
    def refresh_clientdb(self):
        self.clientpane.rulesstore.load_clientdb(self.clientdbload)
    def sync_clientdb(self):
        rules = self.clientpane.rulesstore.convertstore()
        self.clientdbload.set_rules(rules)
    def report_gen(self):
        if self.clientdbload != None:
            try:
                dialog = MonthDialog(self,last_selection=self.last_month-1)
            except:
                currentmonth = exelgen.current_month()
                dialog = MonthDialog(self,last_selection=currentmonth-1)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.sync_clientdb()
                self.last_month = dialog.monthcombo.get_active() + 1
                currentyear = exelgen.current_year()
                excelgenerator = exelgen.Gen(self.clientdbload.pack(), self.last_month)
                rec = filegen.filerec(self.clientdbload.get_full_name(),self.last_month,currentyear)
                savedialog = gtkfileprompt.FileChooserSaveEXCEL(self, reccomended_name=rec)
                save_response = savedialog.run()
                if save_response == Gtk.ResponseType.OK:
                    excelgenerator.report_gen(savedialog.get_filename())
                savedialog.destroy()
            dialog.destroy()
    def add_listing(self):
        if self.clientdbload != None:
            dialog = NewListingDialog(self)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                listing_title = dialog.namefirst.get_text()
                self.clientdbload.append_listing(listing_title,edit=True)
                self.clientpane.rulesstore.append(None, row=(listing_title, 1))
            dialog.destroy()
    def remove_listing(self):
        if self.clientdbload != None:
            iter = self.clientpane.tree.get_selection().get_selected()[1]
            editable = self.clientpane.rulesstore.iter_to_val(iter, 1)
            has_children = self.clientpane.rulesstore.iter_has_child(iter)
            if editable == 1 and not has_children:
                name = self.clientpane.rulesstore.iter_to_val(iter, 0)
                self.clientpane.rulesstore.remove(iter)
                self.clientdbload.remove_listing(name)
            return -1
    def text_edit(self, listing, newname):
        if self.clientdbload != None:
            return self.clientdbload.rename_listing(listing, newname)
        else:
            return -1
if __name__ == '__main__':
    win = MyWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()