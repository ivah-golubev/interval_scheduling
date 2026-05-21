import sqlite3

from enums.Day import Day

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

def select_requests_within_day_interval(cursor: sqlite3.Cursor, day: Day,
                                        start_minute = 0, end_minute = 1440):
    query = """
    SELECT * FROM requests_rooms
    WHERE start_minute >= ? AND end_minute < ? AND day = ?
    """
    cursor.execute(query, (start_minute, end_minute, day.value,))

    return cursor.lastrowid

def select_requests_without_room_building(cursor: sqlite3.Cursor):
    query = """
    SELECT req.req_id, req.course, req.start_minute, req.end_minute, req.day,
        rooms.name, rooms.capacity
    FROM requests AS req
    LEFT JOIN rooms ON req.room_id = rooms.room_id
    WHERE rooms.building IS NULL OR rooms.building = ''
    ORDER BY req.room_id
    """
    cursor.execute(query)

    return cursor.lastrowid

def select_top_rooms_workload_within_day(cursor: sqlite3.Cursor, day: Day, limit = -1):
    if limit == -1:
        query = """
        SELECT room_name, sum(end_minute - start_minute) as total_minutes
        FROM requests_rooms 
        WHERE day = ? AND start_minute < end_minute 
            AND start_minute >= 0 AND end_minute < 1440
        GROUP BY room_id
        ORDER BY total_minutes DESC
        """
        cursor.execute(query, (day.value,))
    else:
        query = """
        SELECT room_name, sum(end_minute - start_minute) as total_minutes
        FROM requests_rooms 
        WHERE day = ? AND start_minute < end_minute
            AND start_minute >= 0 AND end_minute < 1440
        GROUP BY room_id
        ORDER BY total_minutes DESC
        LIMIT ?
        """
        cursor.execute(query, (day.value, limit,))

        return cursor.lastrowid
