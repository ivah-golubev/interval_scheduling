import argparse

import db.db_init as db
import db.db_requests as db_req
import analysis as ans
from enums.Day import Day

parser = argparse.ArgumentParser()
parser.add_argument('--fill_tables', dest='fill_tables', action='store_true')
parser.add_argument('--clear_tables', dest='clear_tables', action='store_true')
parser.add_argument('--print_sql', dest='print_sql', action='store_true')
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

    if args.print_sql:
        print("Запросы в понедельник:")
        db_req.requests_within_day_interval(Day.MONDAY)
        print(*['\t'.join([str(item)[:4].ljust(4) for item in row]) 
                for row in db.cursor.fetchall()], sep='\n')

        print("\nПопулярные курсы:")
        db_req.popular_courses_per_room()
        print(*['\t'.join([str(item).ljust(8) for item in row]) 
                for row in db.cursor.fetchall()], sep='\n')

        print("\nЗапросы, в которых не указано здание аудитории:")
        db_req.requests_without_room_building()
        print(*['\t'.join([str(item).ljust(8) for item in row]) 
                for row in db.cursor.fetchall()], sep='\n')

        print("\nЗагруженность аудиторий в понедельник по убыванию:")
        db_req.top_rooms_workload_within_day(Day.MONDAY)
        print(*['\t'.join([str(item).ljust(8) for item in row]) 
                for row in db.cursor.fetchall()], sep='\n')

        print("\nКоличество запросов в аудиториях по времени суток:")
        db_req.requests_count_per_time_of_day()
        print(*['\t'.join([str(item).ljust(8) for item in row]) 
                for row in db.cursor.fetchall()], sep='\n')

if __name__ == '__main__':
    main()