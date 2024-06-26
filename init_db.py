import sqlite3


def connect_database():
    global conn, cur

    # will connect to db if exists, or create a new one.
    conn = sqlite3.connect('sql_data.db')

    cur = conn.cursor()


def create_database():# first database for hotel booking
    cur.execute('''DROP TABLE IF EXISTS booking;''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "booking" (
            "booking_id"	INTEGER PRIMARY KEY,
            "room" TEXT NOT NULL,
            "guests" TEXT NOT NULL,
            "name"	TEXT NOT NULL,
            "email"	TEXT NOT NULL
            );''')
    
    # second database for inventory management
    cur.execute('''DROP TABLE IF EXISTS items;''')
    cur.execute('''CREATE TABLE IF NOT EXISTS "items" (
            "item_id"	INTEGER PRIMARY KEY,
            "quantity" TEXT NOT NULL,
            "item"	TEXT NOT NULL
            );''')
    

def close_database():
    conn.commit()
    conn.close()


if __name__ == '__main__':
    connect_database()
    create_database()
    close_database()
