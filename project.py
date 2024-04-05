import tkinter as tk
from tkinter import font as tkfont
import tkinter.ttk as ttk  # just for treeview
import entry_field  # no particular good reason I did it the other way here
from models import *  # done this way to access classes just by name
import sys  # only used for flushing debug print statements


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # this is the main database access object
        # note you must run the init_db.py script before using SQLStorage
        self.data = SQLStorage()

        # set a single font to be used throughout the app
        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # all off the frames
        for F in (BrowsePage, ReadPageBooking, ReadPageInventory, CreatePageBooking, CreatePageInventory):
            page_name = F.__name__
            # last arg - send the object that accesses the db
            frame = F(parent=container, controller=self, persist=self.data)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        # program starts off with the browse page
        self.show_frame("BrowsePage")

    def show_frame(self, page_name, rid=0):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        # the edit screen requires knowledge of the id of the item
        if not rid == 0:
            frame.update(rid)
        else:
            frame.update()
        # bring it to the front of the stacking order
        frame.tkraise()


class BrowsePage(tk.Frame):
    ''' the Browse page must show all the items in the database and allow
    access to editing and deleting, as well as the ability to go to a screen
    to add new ones. This is the 'home' screen.
    '''
    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # labels to clarify which treeview is which
        label = tk.Label(self, text="Hotel Booking",
                         font=controller.title_font)
        label.grid(row=0,column=0)

        label = tk.Label(self, text="Hotel Inventory",
                         font=controller.title_font)
        label.grid(row=0,column=1)

        ''' '''
        # set up the treeview for hotel booking
        booking_table = tk.Frame(self, width=100)
        booking_table.grid(row=1,column=0)
        scrollbarx = tk.Scrollbar(booking_table, orient=tk.HORIZONTAL) # scrollbars if necessary
        scrollbary = tk.Scrollbar(booking_table, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(booking_table, columns=("booking_id", "room #", "guests #", "name", "email"),
                                 selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=tk.BOTTOM, fill=tk.X)
        # this section would allow for expanding the viewable columns
        self.tree.heading('booking_id', text="Booking ID", anchor=tk.W)
        self.tree.heading('room #', text="Room #", anchor=tk.W)
        self.tree.heading('guests #', text="# of guests", anchor=tk.W)
        self.tree.heading('name', text="Name", anchor=tk.W)
        self.tree.heading('email', text="Email", anchor=tk.W)
        self.tree.column('#0', stretch=tk.NO, minwidth=0, width=0)
        self.tree.column('#1', stretch=tk.NO, minwidth=0, width=70)
        self.tree.column('#2', stretch=tk.NO, minwidth=0, width=70)
        self.tree.column('#3', stretch=tk.NO, minwidth=0, width=200)
        self.tree.column('#4', stretch=tk.NO, minwidth=0, width=200)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.pack()
        self.selected = []
        
        Inventory_table = tk.Frame(self, width=100)
        Inventory_table.grid(row=1,column=1)
        scrollbarx = tk.Scrollbar(Inventory_table, orient=tk.HORIZONTAL) # scrollbar if necessary
        scrollbary = tk.Scrollbar(Inventory_table, orient=tk.VERTICAL)
        self.treeInventory = ttk.Treeview(Inventory_table, columns=("item_id","quantity", "item"),
                                 selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.treeInventory.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbarx.config(command=self.treeInventory.xview)
        scrollbarx.pack(side=tk.BOTTOM, fill=tk.X)
        # this section would allow for expanding the viewable columns
        self.treeInventory.heading('item_id', text=" Item ID", anchor=tk.W)
        self.treeInventory.heading('quantity', text=" Quantity", anchor=tk.W)
        self.treeInventory.heading('item', text="Item", anchor=tk.W)
        self.treeInventory.column('#0', stretch=tk.NO, minwidth=0, width=0)
        self.treeInventory.column('#1', stretch=tk.NO, minwidth=0, width=100)
        self.treeInventory.column('#2', stretch=tk.NO, minwidth=0, width=100)
        self.treeInventory.bind('<<TreeviewSelect>>', self.on_select)
        self.treeInventory.pack()
        self.selected = []
        
        # this object is the data persistence model
        self.persist = persist
        all_records_booking = self.persist.get_all_sorted_records_booking()
        # grab all records from booking db and add them to the treeview widget
        for record in all_records_booking:
            self.tree.insert("", 0, values=(
                record.rid, record.room, record.guests, record.name, record.email))


        all_records_inventory = self.persist.get_all_sorted_records_inventory()
        # grab all records from inventory db and add them to the treeview widget
        for record in all_records_inventory:
            self.treeInventory.insert("", 0, values=(
                record.rid, record.item, record.quantity))

        # all buttons for editing, deleting, creating records for booking and inventory
        # all listed vertically together
        edit_button_booking = tk.Button(self, text="Edit Record",
                                command=self.edit_selected_booking)
        edit_button_booking.grid(column=0)

        delete_button_booking = tk.Button(self, text="Delete Record(s)",
                                  command=self.delete_selected_booking)
        delete_button_booking.grid(column=0)

        new_button_booking = tk.Button(self, text="Add New Record",
                               command=lambda: controller.show_frame("CreatePageBooking"))
        new_button_booking.grid(column=0)

        
        edit_button_inventory = tk.Button(self, text="Edit Record",
                                command=self.edit_selected_inventory)
        edit_button_inventory.grid(row=2,column=1)

        delete_button_inventory = tk.Button(self, text="Delete Record(s)",
                                  command=self.delete_selected_inventory)
        delete_button_inventory.grid(row=3,column=1)

        new_button_inventory = tk.Button(self, text="Add New Record",
                               command=lambda: controller.show_frame("CreatePageInventory"))
        new_button_inventory.grid(row=4,column=1)

    def edit_selected_booking(self):
        # editing booking records
        idx = self.selected[0]  # use first selected item if multiple
        record_id = self.tree.item(idx)['values'][0]
        self.controller.show_frame("ReadPageBooking", record_id) # switch to editing screen
    
    def edit_selected_inventory(self):
        # editing inventory records
        idx = self.selected[0]  # use first selected item if multiple
        record_id = self.treeInventory.item(idx)['values'][0]
        self.controller.show_frame("ReadPageInventory", record_id) # switch to editing screen

    def on_select(self, event):
        ''' add the currently highlighted items to a list
        '''
        self.selected = event.widget.selection()

    def delete_selected_booking(self):
        ''' uses the selected list to remove and delete certain records
            booking records
        '''
        for idx in self.selected:
            record_id = self.tree.item(idx)['values'][0]
            # remove from the db
            self.persist.delete_record_booking(record_id)
            # remove from the treeview
            self.tree.delete(idx)
    
    def delete_selected_inventory(self):
        ''' uses the selected list to remove and delete certain records
            inventory records
        '''
        for idx in self.selected:
            record_id = self.treeInventory.item(idx)['values'][0]
            # remove from the db
            self.persist.delete_record_inventory(record_id)
            # remove from the treeview
            self.treeInventory.delete(idx)

    def update(self):
        ''' to refresh the treeview, delete all its rows and repopulate from the db 
        '''
        # deletes booking records
        for row in self.tree.get_children():
            self.tree.delete(row)
        # inserts them
        all_records = self.persist.get_all_sorted_records_booking()
        for record in all_records:
            self.tree.insert("", 0, values=(
                record.rid, record.room, record.guests, record.name, record.email))

        # deletes inventory records
        for row in self.treeInventory.get_children():
            self.treeInventory.delete(row)
        # inserts them
        all_records = self.persist.get_all_sorted_records_inventory()
        for record in all_records:
            self.treeInventory.insert("", 0, values=(
                record.rid, record.item, record.quantity))


class ReadPageBooking(tk.Frame):
    ''' same as create page but modified to edit entries
    '''
    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # label to clarify what it is for
        label = tk.Label(self, text="Edit Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button
            all of the fields that users can fill out for booking entries """
        self.data['Room'] = entry_field.EntryField(self, label='Room #')
        self.data['Room'].grid(row=1, column=0, pady=2)

        self.data['Guests'] = entry_field.EntryField(self, label='# of guests')
        self.data['Guests'].grid(row=2, column=0, pady=2)

        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=3, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=4, column=0, pady=2)

        # button to update the entry according to changes made
        self.Button1 = tk.Button(self, text='Update', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=5, column=0, pady=10)

        # return to browse page when user is finished
        button = tk.Button(self, text="Return to the browse page",
                           command=lambda: controller.show_frame("BrowsePage"))
        button.grid(row=6, column=0)

    def update(self, rid):
        record = self.controller.data.get_record_booking(rid)
        # all the fields that booking uses and updates
        self.data['Room'].dataentry.set(record.room)
        self.data["Guests"].dataentry.set(record.guests)
        self.data["Name"].dataentry.set(record.name)
        self.data['Email'].dataentry.set(record.email)
        self.booking = self.persist.get_record_booking(rid)

    def submit(self):
        ''' grab the text placed in the entry widgets accessed through the dict 
            used for booking entries'''
        self.booking.room = self.data['Room'].get()
        self.booking.guests = self.data['Guests'].get()
        self.booking.name = self.data['Name'].get()
        self.booking.email = self.data['Email'].get()
        self.persist.save_record_booking(self.booking)

class ReadPageInventory(tk.Frame):
    ''' similar to ReadPageInventory but for inventory entries
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # label to inform the user this is the editing screen
        label = tk.Label(self, text="Edit Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button
            all the entries for inventory """
        self.data['Item'] = entry_field.EntryField(self, label='Item')
        self.data['Item'].grid(row=1, column=0, pady=2)

        self.data['Quantity'] = entry_field.EntryField(self, label='Quantity')
        self.data['Quantity'].grid(row=2, column=0, pady=2)

        # lets the user commit changes to the entry
        self.Button1 = tk.Button(self, text='Update', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=5, column=0, pady=10)

        # return to browse page when finished
        button = tk.Button(self, text="Return to the browse page",
                           command=lambda: controller.show_frame("BrowsePage"))
        button.grid(row=6, column=0)

    def update(self, rid):
        record = self.controller.data.get_record_inventory(rid)
        # all fields for inventory
        self.data['Item'].dataentry.set(record.item)
        self.data["Quantity"].dataentry.set(record.quantity)
        self.items = self.persist.get_record_inventory(rid)

    def submit(self):
        ''' grab the text placed in the entry widgets accessed through the dict 
            used for inventory entries'''
        self.items.item = self.data['Item'].get()
        self.items.quantity = self.data['Quantity'].get()
        self.persist.save_record_inventory(self.items)

class CreatePageBooking(tk.Frame):
    ''' provides a form for creating a new booking entry
    '''
    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # clarify the new entry screen
        label = tk.Label(self, text="Create New Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button
            fill in the fields for entries  """
        self.data['Room'] = entry_field.EntryField(self, label='Room #')
        self.data['Room'].grid(row=1, column=0, pady=2)

        self.data['Guests'] = entry_field.EntryField(self, label='# of guests')
        self.data['Guests'].grid(row=2, column=0, pady=2)

        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=3, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=4, column=0, pady=2)

        # submit/add a new entry when filled out
        self.Button1 = tk.Button(self, text='Submit', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=5, column=0, pady=10)

        # return to browse page when finished
        button = tk.Button(self, text="Return to the browse page",
                           command=lambda: controller.show_frame("BrowsePage"))
        button.grid(row=6, column=0)

    def reset(self):
        ''' on every new entry, blank out the fields
        '''
        for key in self.data:
            self.data[key].reset()

    def update(self):
        self.reset()

    def submit(self):
        ''' make a new contact based on the form using whatever the user input
        '''
        b = Booking(name=self.data['Name'].get(),
                    room=self.data['Room'].get(),
                    guests=self.data['Guests'].get(),
                    email=self.data['Email'].get())
        self.persist.save_record_booking(b)
        self.update()

class CreatePageInventory(tk.Frame):
    ''' provides a form for creating a new Contact
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # clarify the new entry screen
        label = tk.Label(self, text="Create New Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button
            fields for user to fill"""
        self.data['Item'] = entry_field.EntryField(self, label='Item')
        self.data['Item'].grid(row=1, column=0, pady=2)

        self.data['Quantity'] = entry_field.EntryField(self, label='Quantity')
        self.data['Quantity'].grid(row=2, column=0, pady=2)

        # add the new entry when finished
        self.Button1 = tk.Button(self, text='Submit', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=3, column=0, pady=10)

        # return to browse page when finished
        button = tk.Button(self, text="Return to the browse page",
                           command=lambda: controller.show_frame("BrowsePage"))
        button.grid(row=4, column=0)

    def reset(self):
        ''' on every new entry, blank out the fields
        '''
        for key in self.data:
            self.data[key].reset()

    def update(self):
        self.reset()

    def submit(self):
        ''' make a new contact based on the form using whatever the user input
        '''
        i = Inventory(item=self.data['Item'].get(),
                    quantity=self.data['Quantity'].get())
        self.persist.save_record_inventory(i)
        self.update()


if __name__ == "__main__":
    app = App()
    app.mainloop()
