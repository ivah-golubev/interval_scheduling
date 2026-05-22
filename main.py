import argparse

import db.db_init as db

parser = argparse.ArgumentParser()
parser.add_argument('--fill_tables', dest='fill_tables', action='store_true')
parser.add_argument('--clear_tables', dest='clear_tables', action='store_true')
args = parser.parse_args()

def main():
    db.create_rooms_table()
    db.conn.commit()

    db.create_requests_table()
    db.conn.commit()
    
    if args.fill_tables:
        db.fill_rooms_table()
        db.conn.commit()
        
        db.fill_requests_table()
        db.conn.commit()

    elif args.clear_tables:
        db.clear_rooms_table()
        db.conn.commit()
        
        db.clear_requests_table()
        db.conn.commit()

    db.create_requests_rooms_view()
    db.conn.commit()


if __name__ == '__main__':
    main()