from matplotlib import pyplot as plt
import pandas as pd
import db.db_init as db
import db.db_queries as db_q
from enums.Day import Day

def validate_time_bounds(df: pd.DataFrame) -> pd.DataFrame:
    if not 'start_minute' in df.columns or not 'end_minute' in df.columns:
        return df
    
    mask1 = df['end_minute'] > df['start_minute']
    mask2 = df['start_minute'].between(0, 1440)
    mask3 = df['end_minute'].between(0, 1440)

    df = df.loc[mask1 & mask2 & mask3]

    return df

def validate_null_values(df: pd.DataFrame) -> pd.DataFrame:
    # na_rows = df.loc[df.isna().any(axis=1)]
    
    if 'start_minute' in df.columns and 'end_minute' in df.columns:
        df = df.dropna(subset=['start_minute', 'end_minute'])

    if 'course' in df.columns:
        df['course'] = df['course'].fillna('undefined')
    if 'room_name' in df.columns:
        df['room_name'] = df['room_name'].fillna('undefined')
    if 'room_capacity' in df.columns:
        df['room_capacity'] = df['room_capacity'].fillna(0)
    if 'room_building' in df.columns:
        df['room_building'] = df['room_building'].fillna('undefined')

    return df

def get_requests_within(day: Day, start_minute = 0, end_minute = 1440) -> pd.DataFrame:
    df = pd.read_sql_query(db_q.requests_within_day_interval_query, 
                           db.conn, index_col='req_id', 
                           params=(start_minute, end_minute, day))
    
    df.drop_duplicates(inplace=True)
    df = validate_null_values(df)
    df = validate_time_bounds(df)
    
    return df

def get_rooms_time_stats(day: Day, start_minute = 0, end_minute = 1440) -> pd.DataFrame:
    df = get_requests_within(day, start_minute, end_minute)
    df['time_interval'] = df['end_minute'] - df['start_minute']

    stats = df.groupby(by=['room_id', 'room_name']).agg(
            first_lesson_start=('start_minute', 'min'), 
            first_lesson_end=('end_minute', 'min'), 
            last_lesson_start=('start_minute', 'max'),
            last_lesson_end=('end_minute', 'max'),
            avg_start=('start_minute', 'mean'),
            avg_end=('end_minute', 'mean'),
            min_lesson_duration=('time_interval', 'min'),
            max_lesson_duration=('time_interval', 'max'),
            avg_lesson_duration=('time_interval', 'mean')
    ).round(2)

    return stats

def get_rooms_workload_by_hours(day: Day):
    df = get_requests_within(day)
    df['current_hour'] = df['start_minute'] // 60
    df['end_hour'] = df['end_minute'] // 60
    
    df_add = df.copy()
    while(df_add.shape[0]):
        df_add['current_hour'] += 1
        df_add = df_add.loc[df_add['current_hour'] <= df_add['end_hour']]
        df = pd.concat([df, df_add], ignore_index=True)

    df = df.groupby(['room_id', 'room_name', 'current_hour']) \
        .size().reset_index(name='workload')
    # df = df.pivot(columns='current_hour', index='room_name', values='workload')
    # df = df.fillna(0).astype('int32')
    
    return df

def get_rooms_courses_count(multiplier = 1) -> pd.DataFrame:
    df = pd.read_sql_query(db_q.popular_courses_per_room_query, 
                           db.conn, index_col='req_id', 
                           params=(1 - multiplier,))
    
    df = df.pivot(index='room_name', columns='course', values='course_count')
    df = df.fillna(0).astype('int32')
    
    return df

def get_popular_courses() -> pd.DataFrame:
    df = get_rooms_courses_count()
    return df.sum().reset_index(name='requests_count') \
        .sort_values(by='requests_count', ignore_index=True, ascending=False)

def get_all_rooms() -> pd.DataFrame:
    df = pd.read_sql_query('SELECT * FROM rooms', db.conn, index_col='room_id')
    
    if 'name' in df.columns:
        df['name'] = df['name'].fillna('undefined')
    if 'building' in df.columns:
        df['building'] = df['building'].fillna('undefined')
    if 'capacity' in df.columns:
        df['capacity'] = df['capacity'].fillna(0)

    return validate_null_values(df)

def get_requests_rooms_all(day: Day, start_minute = 0, end_minute = 1440) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_requests_rooms = get_requests_within(day, start_minute, end_minute)
    df_rooms = get_all_rooms()

    df_merged = df_requests_rooms.merge(df_rooms, 'right', on='room_id')
    return df_merged[df_requests_rooms.columns.to_list()], df_requests_rooms, df_rooms 

def get_rooms_without_requests(day: Day, start_minute = 0, end_minute = 1440) -> pd.DataFrame:
    df_merged, df_requests_rooms, df_rooms = get_requests_rooms_all(day, start_minute, end_minute)

    cond = ~df_merged.apply(tuple, axis=1).isin(df_requests_rooms.apply(tuple, axis=1))
    return df_rooms[df_rooms.index.isin(df_merged[cond]['room_id'])]

def get_all_requests() -> pd.DataFrame:
    df = pd.read_sql_query("SELECT * FROM requests_rooms", 
                           db.conn, index_col='req_id')
    
    df.drop_duplicates(inplace=True)
    df = validate_null_values(df)
    df = validate_time_bounds(df)

    return df

def draw_requests_count_by_day():
    df = get_all_requests()

    df = df.groupby('day').size().reset_index(name='req_count')
    
    df.plot.bar(x='day', y='req_count')
    plt.tight_layout()
    plt.savefig('report/req_count_by_day.png')
    plt.show()

def draw_requests_count_distribution(day: Day):
    df = get_rooms_workload_by_hours(day)

    print(df)

    df_add = df.copy()
    while(df_add.shape[0]):
        df_add['workload'] -= 1
        df_add = df_add.loc[df_add['workload'] >= 0]
        df = pd.concat([df, df_add], ignore_index=True)

    df.rename(columns={'current_hour': 'requests_count'}, inplace=True)

    df[['requests_count']].plot.hist(
        title=f'Requests count ({day.value})', legend=False,
        xlabel='Hours', ylabel='Requests Count')
    
    plt.tight_layout()
    plt.savefig('report/req_count_distribution.png')
    plt.show()

def workload_by_hours_and_rooms(day: Day, room_count_x = 2, room_count_y = 3):
    df = get_rooms_workload_by_hours(day)

    fig, axes = plt.subplots(room_count_x, room_count_y)

    rooms = list(df['room_name'].unique())[:room_count_x * room_count_y]

    for x in range(room_count_x):
        for y in range(room_count_y):
            room_name = rooms[y * room_count_x + x]
            df.loc[df['room_name'] == room_name].plot(
                    ax=axes[x, y], x='current_hour', y='workload', 
                    sharex=False, sharey=False, title=room_name,
                    xlabel='hours', legend=None, figsize=(10, 6))
    
    fig.suptitle(f'Requests count by hours and rooms ({day.value})')
    fig.tight_layout()
    fig.savefig('report/req_count_by_hours_and_rooms.png')
    plt.show()