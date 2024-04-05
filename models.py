import shelve
import sqlite3


class SQLStorage():
    ''' Represents a persistence layer provided using sqlite
    '''
    FILENAME = "sql_data.db"

    def __init__(self):
        ''' initiate access to the data persistence layer
        '''
        self.conn = sqlite3.connect(self.FILENAME)
        self.data_access = self.conn.cursor()
        # data_access is now a cursor object

    def get_record_booking(self, rid):
        ''' return a single record identified by the record id
            takes the data from the columns in the hotel booking database
        '''
        self.data_access.execute(
            """SELECT * from booking WHERE booking_id= ?;""", (rid,))
        row = self.data_access.fetchone()
        booking = Booking(row[1], row[2], row[3], row[4], row[0])
        return booking

    def get_all_records_booking(self):
        ''' return all records stored in the hotel booking database
        '''
        self.data_access.execute("""SELECT * from booking;""")
        booking = []    # adds all of the records in a list
        for row in self.data_access:
            booking.append(
                Booking(row[1], row[2], row[3], row[4], row[0]))
        return booking

    def save_record_booking(self, record):
        ''' add a record represented by a dict with a new id
            saves new records and edited records for hotel booking
        '''
        if record.rid == 0:     # if new record:
            self.data_access.execute("""INSERT INTO booking(room, guests, name, email) VALUES (?,?,?,?)
            """, (record.room, record.guests, record.name, record.email))
            record.rid = self.data_access.lastrowid
        else:   # if old record / updating a record
            self.data_access.execute("""UPDATE booking SET room = ?, guests = ?,name = ?, email = ?
            WHERE booking_id = ?""", (record.room, record.guests, record.name, record.email, record.rid))
        self.conn.commit()

    def get_all_sorted_records_booking(self): # sorts the records for hotel booking
        return sorted(self.get_all_records_booking(), key=lambda x: x.rid)

    def delete_record_booking(self, rid):
        # delete record for hotel booking
        # convert to int since value comes from treeview (str)
        self.data_access.execute("""DELETE FROM booking WHERE booking_id = ?""",
                                 (int(rid),))
        self.conn.commit()
    
    def delete_record_inventory(self, rid):
        # delete record for inventory
        # convert to int since value comes from treeview (str)
        self.data_access.execute("""DELETE FROM items WHERE item_id = ?""",
                                 (int(rid),))
        self.conn.commit()

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity
        '''
        if (self.data_access):
            self.conn.commit()
            self.data_access.close()



    # inventory records need their own functions since they have different parameters than booking
    def get_record_inventory(self, rid):
        ''' return a single record identified by the record id
            takes the data from the columns in the inventory database
        '''
        self.data_access.execute(
            """SELECT * from items WHERE item_id= ?;""", (rid,))
        row = self.data_access.fetchone()
        items = Inventory(row[1], row[2], row[0])
        return items

    def get_all_records_inventory(self):
        ''' return all records stored in the inventory database
        '''
        self.data_access.execute("""SELECT * from items;""")
        items = []      # adds all of the records in a list
        for row in self.data_access:
            items.append(
                Inventory(row[1], row[2], row[0]))
        return items
    
    def save_record_inventory(self, record):
        ''' add a record represented by a dict with a new id
            saves new records and edited records for the inventory
        '''
        if record.rid == 0:     # if new record
            self.data_access.execute("""INSERT INTO items(item, quantity) VALUES (?,?)
            """, (record.item, record.quantity))
            record.rid = self.data_access.lastrowid
        else:   # if old record/ updating record
            self.data_access.execute("""UPDATE items SET item = ?, quantity = ?
            WHERE item_id = ?""", (record.item, record.quantity, record.rid))
        self.conn.commit()

    def get_all_sorted_records_inventory(self): # sorts all inventory records
        return sorted(self.get_all_records_inventory(), key=lambda x: x.rid)



class ShelveStorage():
    ''' Represents a simple persistence layer provided using the shelve module
    which pickles objects into a dbm
    '''
    FILENAME = "project_data.db"

    def __init__(self):
        ''' initiate access to the data persistence layer
        '''
        # using writeback is slower but avoids some weird caching issues
        self.data_access = shelve.open(self.FILENAME, writeback=True)

    def get_record(self, rid):
        ''' return a single record identified by the record id
        '''
        record_id = "record" + str(rid)
        return self.data_access[record_id]

    def get_all_records(self):
        ''' return all records stored in the database
        '''
        return list(self.data_access.values())

    def save_record(self, record):
        ''' add a record represented by a dict with a new id
        '''
        # if it's still 0 then it's a new record, otherwise it's not
        if record.rid == 0:
            record.rid = self.get_new_id()

        record_key = "record" + str(record.rid)

        # needs to be an string key for the dict
        self.data_access[record_key] = record

    def get_all_sorted_records(self):
        return sorted(self.get_all_records(), key=lambda x: x.rid)

    def delete_record(self, rid):
        del self.data_access["record" + str(rid)]

    def get_new_id(self):
        all_sorted_records = self.get_all_sorted_records()
        if len(all_sorted_records) == 0:
            return 1
        else:
            return int(self.get_all_sorted_records()[-1].rid) + 1
# edge case if all are deleted after creation, what is the safe number?

    def cleanup(self):
        ''' call this before the app closes to ensure data integrity
        '''
        self.data_access.close()


class Booking(): # everything that booking entries will have
    def __init__(self, room ="", guests="", name="", email="", rid=0):
        self.rid = rid  # 0 represents a new, unsaved record; will get updated
        self.room = room
        self.guests = guests
        self.name = name
        self.email = email

    def __str__(self):
        return f'Booking#: {self.rid}; Room: {self.room},Guests: {self.guests}, Name: {self.name}, Email: {self.email}'

class Inventory(): # eevrything that inventory entries will have
    def __init__(self, item ="", quantity="", rid=0):
        self.rid = rid  # 0 represents a new, unsaved record; will get updated
        self.item = item
        self.quantity = quantity

    def __str__(self):
        return f'Inventory#: {self.rid}; Item: {self.item},quantity: {self.quantity}'
