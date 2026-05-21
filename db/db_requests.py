import sqlite3

from enums.Day import Day

def select_requests_by_day(cursor: sqlite3.Cursor, day: Day):
    query = """
    SELECT * FROM requests_rooms
    WHERE lower(day) = ?
    """
    cursor.execute(query, (day.value,))
    
    return cursor.lastrowid