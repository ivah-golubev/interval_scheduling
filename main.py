import sqlite3

import db

def main():
    db_name = 'requests_rooms.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    db.create_rooms_table(cursor)
    conn.commit()

    db.create_requests_table(cursor)
    conn.commit()

    db.fill_rooms_table(cursor)
    conn.commit()
    
    db.fill_requests_table(cursor)
    conn.commit()

if __name__ == '__main__':
    main()