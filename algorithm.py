import pandas as pd

from enums.Day import Day
from analysis import get_requests_within

def get_room_schedule(room_id, day):
    df = get_requests_within(day).sort_values(by='end_minute')
    df = df[df['room_id'] == room_id]
    
    return df

def max_schedule(room_id, day: Day) -> pd.DataFrame:
    df = get_room_schedule(room_id, day)
    result = []

    while(df.shape[0]):
        result.append(df.iloc[0])
        df = df[df['start_minute'] >= result[-1]['end_minute']]

    return pd.DataFrame(result)

def max_schedule_2(room_id, day: Day) -> pd.DataFrame:
    df = get_room_schedule(room_id, day)

    if df.empty: return df

    result = [ df.iloc[0] ]

    current_end_minute = result[0]['end_minute']

    for i in range(1, df.shape[0]):
        row = df.iloc[i]
        if row['start_minute'] >= current_end_minute:
            current_end_minute = row['end_minute']
            result.append(row)

    return pd.DataFrame(result)

def max_schedule_bin_sch(room_id, day: Day) -> pd.DataFrame:
    df = get_room_schedule(room_id, day)

    if df.empty: return df

    result = [ df.iloc[0] ]

    current_end_minute = result[0]['end_minute']

    outer_start = 0
    while True:
        start, end = outer_start, df.shape[0] - 2
        while True:
            if start > end: return pd.DataFrame(result)
            middle = start + (end - start) // 2
            row1 = df.iloc[middle]

            if row1['start_minute'] >= current_end_minute:
                end = middle
                continue

            row2 = df.iloc[middle + 1]

            if row2['start_minute'] >= current_end_minute:
                current_end_minute = row2['end_minute']
                result.append(row2)
                outer_start = middle + 1
                break
            else:
                start = middle + 1
                continue