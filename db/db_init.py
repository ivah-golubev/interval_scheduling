import sqlite3
import csv
import sys
from typing import Callable, Iterable

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

def fill_table(cursor: sqlite3.Cursor, filename, query: str, fields: set,
               get_row_data: Callable[[Iterable], tuple]) -> int | None:
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

def fill_rooms_table(cursor: sqlite3.Cursor, 
                     filename = 'csv/rooms.csv') -> int | None:
    fields = { 'room_id', 'name', 'capacity', 'building' }
    
    get_rooms_data = lambda row: (
        int(row['room_id']), row['name'], 
        int(row['capacity'] or 0), row['building']
        )
    
    query = """
    INSERT INTO rooms (room_id, name, capacity, building)
    VALUES (?, ?, ?, ?)
    """

    return fill_table(cursor, filename, query, fields, get_rooms_data)

def fill_requests_table(cursor: sqlite3.Cursor, 
                        filename = 'csv/requests.csv') -> int | None:
    fields = {
        'req_id', 'room_id', 'course', 
        'start_minute', 'end_minute', 'day' }
    
    get_requests_data = lambda row: (
        int(row['req_id']), int(row['room_id']), row['course'],
        int(row['start_minute'] or 0), int(row['end_minute'] or 0), row['day']
        )
    
    query = """
    INSERT INTO requests (
        req_id, room_id, course, 
        start_minute, end_minute, day
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    return fill_table(cursor, filename, query, fields, get_requests_data)

def clear_rooms_table(cursor: sqlite3.Cursor):
    cursor.execute("DELETE FROM rooms")

def clear_requests_table(cursor: sqlite3.Cursor):
    cursor.execute("DELETE FROM requests")