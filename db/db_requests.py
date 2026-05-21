import sqlite3

from enums.Day import Day

def select_requests_by_day(cursor: sqlite3.Cursor, day: Day):
    query = """
    SELECT * FROM requests_rooms
    WHERE day = ?
    """
    cursor.execute(query, (day.value,))
    
    return cursor.lastrowid

def select_popular_courses_per_room(cursor: sqlite3.Cursor, multiplier):
    query = """
    SELECT room_name, course, count(course) as course_count
    FROM requests_rooms GROUP BY room_id, course HAVING course_count > ( SELECT (
        SELECT count(course) as room_course_count
        FROM requests_rooms AS rr
        WHERE rr.room_id = room_id
        GROUP BY rr.room_id, rr.course
        ORDER BY rr.room_id, room_course_count DESC
        LIMIT 1
    ) * ? )
    ORDER BY room_id, course_count DESC

    """
    cursor.execute(query, (1 - multiplier,))

    return cursor.lastrowid