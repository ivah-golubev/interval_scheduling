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

