import sqlite3
import argparse

import db.db_init as db
import db.db_requests as db_req
from enums.Day import Day

parser = argparse.ArgumentParser()
parser.add_argument('--fill_tables', dest='fill_tables', action='store_true')
parser.add_argument('--clear_tables', dest='clear_tables', action='store_true')
args = parser.parse_args()

def main():

    db_name = 'requests_rooms.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    db.create_rooms_table(cursor)
    conn.commit()

    db.create_requests_table(cursor)
    conn.commit()
    
    if args.fill_tables:
        db.fill_rooms_table(cursor)
        conn.commit()
        
        db.fill_requests_table(cursor)
        conn.commit()

    elif args.clear_tables:
        db.clear_rooms_table(cursor)
        conn.commit()
        
        db.clear_requests_table(cursor)
        conn.commit()

    db.create_requests_rooms_view(cursor)
    conn.commit()

    db_req.select_requests_by_day(cursor, Day.TUESDAY)
    print(*cursor.fetchall(), sep='\n')

if __name__ == '__main__':
    main()