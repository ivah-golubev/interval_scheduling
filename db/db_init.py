import sqlite3
import csv
import sys
from typing import Callable, Iterable

db_name = 'requests_rooms.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

def create_rooms_table(cursor: sqlite3.Cursor = cursor):
    query = """
    CREATE TABLE IF NOT EXISTS rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        capacity INTEGER, 
        building TEXT
    )"""
    cursor.execute(query)

def create_requests_table(cursor: sqlite3.Cursor = cursor):
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
    
    idx_query = "CREATE INDEX IF NOT EXISTS idx_requests_day ON requests (day)"
    cursor.execute(idx_query)

def fill_table(filename, query: str, fields: set,
               get_row_data: Callable[[Iterable], tuple],
               cursor: sqlite3.Cursor = cursor) -> int | None:
    try:
        with open(filename, 'r') as fin: 
            fin_csv = csv.DictReader(fin)
            
            if not fin_csv.fieldnames:
                raise csv.Error(f"{filename} не содержит столбцов")
            
            fieldnames = fin_csv.fieldnames
            fieldnames_set = set(fieldnames)

            missing_fields = fields - fieldnames_set
            if len(missing_fields) > 0: 
                msg = f"{filename} не содержит столбцы: {', '.join(missing_fields)}"
                raise csv.Error(msg)
            
            if len(fieldnames_set) < len(fieldnames):
                raise csv.Error(f"{filename} содержит дублирующиеся столбцы")

            rows_to_insert = [ get_row_data(row) for row in fin_csv ]

        cursor.executemany(query, rows_to_insert)
    except IOError:
        print(f"Не удалось открыть/прочитать файл {filename}")
        sys.exit()
    except sqlite3.IntegrityError as e:
        print(f"Нарушение целостности: {e}")
    except csv.Error as e:
        print(f"Ошибка обработки CSV: {e}")
    except ValueError as e:
        print(f"Неверный тип данных или пустое значение в столбце: {e}")

    return cursor.lastrowid

def fill_rooms_table(filename = 'csv/rooms.csv',
                     cursor: sqlite3.Cursor = cursor) -> int | None:
    fields = { 'room_id', 'name', 'capacity', 'building' }
    
    get_rooms_data = lambda row: (
        int(row['room_id']) if row['room_id'] else None, 
        row['name'].lower().strip() or None, 
        int(row['capacity']) if row['capacity'] else None, 
        row['building'].lower().strip() or None
        )
    
    query = """
    INSERT INTO rooms (room_id, name, capacity, building)
    VALUES (?, ?, ?, ?)
    """

    return fill_table(filename, query, fields, get_rooms_data, cursor)

def fill_requests_table(filename = 'csv/requests.csv',
                        cursor: sqlite3.Cursor = cursor) -> int | None:
    fields = {
        'req_id', 'room_id', 'course', 
        'start_minute', 'end_minute', 'day' }
    
    get_requests_data = lambda row: (
        int(row['req_id']) if row['req_id'] else None, 
        int(row['room_id']) if row['room_id'] else None, 
        row['course'].lower().strip() or None,
        int(row['start_minute']) if row['start_minute'] else None, 
        int(row['end_minute']) if row['end_minute'] else None, 
        row['day'].lower().strip() or None
        )
    
    query = """
    INSERT INTO requests (
        req_id, room_id, course, 
        start_minute, end_minute, day
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    return fill_table(filename, query, fields, get_requests_data, cursor)

def create_requests_rooms_view(cursor: sqlite3.Cursor = cursor):
    query = """
    CREATE VIEW IF NOT EXISTS requests_rooms
    AS
    SELECT req.*, 
        rooms.name AS room_name, 
        rooms.capacity AS room_capacity, 
        rooms.building AS room_building
    FROM requests as req
    INNER JOIN rooms ON req.room_id = rooms.room_id
    """
    cursor.execute(query)

def clear_rooms_table(cursor: sqlite3.Cursor = cursor):
    cursor.execute("DELETE FROM rooms")

def clear_requests_table(cursor: sqlite3.Cursor = cursor):
    cursor.execute("DELETE FROM requests")