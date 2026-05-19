import sqlite3

def create_rooms_table(cursor: sqlite3.Cursor):
    query = """
    CREATE TABLE IF NOT EXISTS rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        capacity INTEGER, 
        building TEXT
    )"""
    cursor.execute(query)

def create_requests_table(cursor: sqlite3.Cursor):
    query = """
    CREATE TABLE IF NOT EXISTS requests (
        req_id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        course TEXT,
        start_minute INTEGER,
        end_minute INTEGER,
        day TEXT,

        FOREIGN KEY (room_id) REFERENCES rooms (room_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    )"""
    cursor.execute(query)
