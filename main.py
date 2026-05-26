import argparse

import db.db_init as db
import db.db_queries as db_q

import analysis as ans
import algorithm as alg

from enums.Day import Day

parser = argparse.ArgumentParser()
parser.add_argument('--fill_tables', dest='fill_tables', action='store_true', default=True)
parser.add_argument('--clear_tables', dest='clear_tables', action='store_true')
args = parser.parse_args()
delimiter_str = '-' * 50

def print_sql():
    print(delimiter_str)
    print("Запросы в понедельник:")
    print(delimiter_str)
    db_q.requests_within_day_interval(Day.MONDAY)
    print('\t'.join([str(item[0]).ljust(8) for item in db.cursor.description[:-3]]))
    print(*['\t'.join([str(item).ljust(8) for item in row[:-3]]) 
            for row in db.cursor.fetchall()], sep='\n')

    print()
    print(delimiter_str)
    print("Популярные курсы:")
    print(delimiter_str)
    db_q.popular_courses_per_room()
    print('\t'.join([str(item[0]).ljust(8) for item in db.cursor.description]))
    print(*['\t'.join([str(item).ljust(8) for item in row]) 
            for row in db.cursor.fetchall()], sep='\n')

    print()
    print(delimiter_str)
    print("Запросы, в которых не указано здание аудитории:")
    print(delimiter_str)
    db_q.requests_without_room_building()
    print('\t'.join([str(item[0]).ljust(8) for item in db.cursor.description]))
    print(*['\t'.join([str(item).ljust(8) for item in row]) 
            for row in db.cursor.fetchall()], sep='\n')

    print()
    print(delimiter_str)
    print("Загруженность аудиторий в понедельник по убыванию:")
    print(delimiter_str)
    db_q.top_rooms_workload_within_day(Day.MONDAY)
    print('\t'.join([str(item[0]).ljust(8) for item in db.cursor.description]))
    print(*['\t'.join([str(item).ljust(8) for item in row]) 
            for row in db.cursor.fetchall()], sep='\n')

    print()
    print(delimiter_str)
    print("Количество запросов в аудиториях по времени суток:")
    print(delimiter_str)
    db_q.requests_count_per_time_of_day()
    print('\t'.join([str(item[0]).ljust(8) for item in db.cursor.description]))
    print(*['\t'.join([str(item).ljust(8) for item in row]) 
            for row in db.cursor.fetchall()], sep='\n')

def print_pandas():
    print()
    print(delimiter_str)
    print(
        "Занятия в понедельник (после валидации временных интервалов, " 
        "пустых значений и повторяющихся строк):"
    )
    print(delimiter_str)
    print(ans.get_requests_within(Day.MONDAY))

    print()
    print(delimiter_str)
    print("Загруженность (кол-во занятий в час) аудиторий по часам во вторник:")
    print(delimiter_str)
    print(ans.get_rooms_workload_by_hours(Day.TUESDAY))

    print()
    print(delimiter_str)
    print("Популярность (по кол-ву запросов) курсов в аудиториях:")
    print(delimiter_str)
    print(ans.get_rooms_courses_count())

    print()
    print(delimiter_str)
    print("Популярность (по кол-ву запросов) курсов:")
    print(delimiter_str)
    print(ans.get_popular_courses())

    print()
    print(delimiter_str)
    print("Незагруженные аудитории в среду (т.е. без запросов):")
    print(delimiter_str)
    print(ans.get_rooms_without_requests(Day.WEDNESDAY))

def print_plots():
    ans.draw_requests_count_by_day()
    ans.draw_requests_count_distribution(Day.THURSDAY)
    ans.draw_workload_by_hours_and_rooms(Day.FRIDAY)

def print_alg():
    print()
    print(delimiter_str)
    print("Исходное расписание для аудитории 1 в понедельник:")
    print(delimiter_str)
    print(alg.get_room_schedule(1, Day.MONDAY))

    print()
    print("Максимальное непересекающееся расписание:")
    print(alg.max_schedule(1, Day.MONDAY))

    print()
    print(delimiter_str)
    print("Исходное расписание для аудитории 5 во вторник:")
    print(delimiter_str)
    print(alg.get_room_schedule(5, Day.TUESDAY))

    print()
    print("Максимальное непересекающееся расписание:")
    print(alg.max_schedule(5, Day.TUESDAY))

    print()
    print(delimiter_str)
    print("Исходное расписание для аудитории 8 во среду:")
    print(delimiter_str)
    print(alg.get_room_schedule(8, Day.WEDNESDAY))

    print()
    print("Максимальное непересекающееся расписание:")
    print(alg.max_schedule(8, Day.WEDNESDAY))

    print()
    print(delimiter_str)
    print("Исходное расписание для аудитории 3 во четверг:")
    print(delimiter_str)
    print(alg.get_room_schedule(3, Day.THURSDAY))

    print()
    print("Максимальное непересекающееся расписание:")
    print(alg.max_schedule(3, Day.THURSDAY))

    print()
    print(delimiter_str)
    print("Исходное расписание для аудитории 2 во пятницу:")
    print(delimiter_str)
    print(alg.get_room_schedule(2, Day.FRIDAY))

    print()
    print("Максимальное непересекающееся расписание:")
    print(alg.max_schedule(2, Day.FRIDAY))

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

    while(True):
        print("1 - Запросы SQL")
        print("2 - Анализ")
        print("3 - Графики")
        print("4 - Алг. задача (максимальное расписание)")
        print("5 - Выход")
        print("Выберите задание из списка выше: ", end='')

        command = input()
        match command:
            case '1': print_sql()
            case '2': print_pandas()
            case '3': print_plots()
            case '4': print_alg()
            case '5': break
            case _: print("Неверный ввод")
        print()

if __name__ == '__main__':
    main()