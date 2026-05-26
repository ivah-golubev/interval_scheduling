import pandas as pd

from enums.Day import Day
from analysis import get_requests_within

def max_schedule(room_id, day: Day) -> pd.DataFrame:
    df = get_requests_within(day).sort_values(by='end_minute')
    df = df[df['room_id'] == room_id]

    result = []

    while(df.shape[0]):
        result.append(df.iloc[0])
        df = df[df['start_minute'] >= result[-1]['end_minute']]

    return pd.DataFrame(result)