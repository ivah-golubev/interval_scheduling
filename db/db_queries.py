import sqlite3

from enums.Day import Day
import db.db_init as db

requests_within_day_interval_query = """
SELECT * FROM requests_rooms
WHERE start_minute >= ? AND end_minute < ? AND day = ?
"""

popular_courses_per_room_query = """
SELECT req_id, room_name, course, count(course) as course_count
FROM requests_rooms 
GROUP BY room_id, course HAVING course_count > ( SELECT (
    SELECT count(course) as room_course_count
    FROM requests_rooms AS rr
    WHERE rr.room_id = room_id
    GROUP BY rr.room_id, rr.course
    ORDER BY rr.room_id, room_course_count DESC
    LIMIT 1
) * ? )
ORDER BY room_id, room_name, course_count DESC
"""

requests_without_room_building_query = """
SELECT req.req_id, req.course, req.start_minute, req.end_minute, req.day,
    rooms.name, rooms.capacity
FROM requests AS req
LEFT JOIN rooms ON req.room_id = rooms.room_id
WHERE rooms.building IS NULL
ORDER BY req.room_id
"""

top_rooms_workload_within_day_query = """
SELECT room_name, sum(end_minute - start_minute) as total_minutes
FROM requests_rooms 
WHERE day = ? AND start_minute < end_minute 
    AND start_minute >= 0 AND end_minute < 1440
GROUP BY room_id
ORDER BY total_minutes DESC
"""

top_rooms_workload_within_day_limit_query = """
SELECT room_name, sum(end_minute - start_minute) as total_minutes
FROM requests_rooms 
WHERE day = ? AND start_minute < end_minute
    AND start_minute >= 0 AND end_minute < 1440
GROUP BY room_id
ORDER BY total_minutes DESC
LIMIT ?
"""

requests_count_per_time_of_day_query = """
SELECT room_name,
CASE
    WHEN start_minute >= 0 AND start_minute < 240 THEN 'night'
    WHEN start_minute >= 240 AND start_minute < 480 THEN 'morning'
    WHEN start_minute >= 480 AND start_minute < 720 THEN 'late_morning'
    WHEN start_minute >= 720 AND start_minute < 960 THEN 'day'
    WHEN start_minute >= 960 AND start_minute < 1200 THEN 'evening'
    WHEN start_minute >= 1200 AND start_minute < 1440 THEN 'late_evening'
    ELSE 'undefined' END time_of_day,
count(*) AS requests_count
FROM requests_rooms
WHERE start_minute >= 0 AND end_minute < 1440 AND start_minute < end_minute
GROUP BY room_name, time_of_day
ORDER BY room_name, requests_count DESC
"""


def requests_within_day_interval(day: Day, start_minute=0, end_minute=1440,
                                 cursor: sqlite3.Cursor = db.cursor):
    cursor.execute(requests_within_day_interval_query,
                   (start_minute, end_minute, day.value,))

    return cursor.lastrowid


def popular_courses_per_room(multiplier=0.1, cursor: sqlite3.Cursor = db.cursor):
    cursor.execute(popular_courses_per_room_query, (1 - multiplier,))

    return cursor.lastrowid


def requests_without_room_building(cursor: sqlite3.Cursor = db.cursor):
    cursor.execute(requests_without_room_building_query)

    return cursor.lastrowid


def top_rooms_workload_within_day(day: Day, limit=-1,
                                  cursor: sqlite3.Cursor = db.cursor):
    if limit == -1:
        cursor.execute(top_rooms_workload_within_day_query, (day.value,))
    else:
        cursor.execute(top_rooms_workload_within_day_limit_query,
                       (day.value, limit,))

    return cursor.lastrowid


def requests_count_per_time_of_day(cursor: sqlite3.Cursor = db.cursor):
    cursor.execute(requests_count_per_time_of_day_query)

    return cursor.lastrowid