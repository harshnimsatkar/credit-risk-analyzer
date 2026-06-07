import pandas as pd

def add_velocity_features(df):
    df = df.sort_values(['cc_num','unix_time'])
    df['prev_unix_1'] = df.groupby('cc_num')['unix_time'].shift(1)
    df['prev_unix_4'] = df.groupby('cc_num')['unix_time'].shift(4)
    df['time_diff_1'] = df['unix_time'] - df['prev_unix_1']
    df['time_diff_4'] = df['unix_time'] - df['prev_unix_4']
    df['velocity_flag'] = df['time_diff_4'].apply(
        lambda x: 2 if pd.notna(x) and x <= 3600 else (
                  1 if pd.notna(x) and x <= 7200 else 0))
    return df

def add_risk_score(df):
    df['risk_score'] = (
        df['is_night'] +
        df['is_high_risk_merchant'] +
        df['velocity_flag'].apply(lambda x: 1 if x == 2 else 0) +
        df['is_high_amount']
    )
    df['risk_tier'] = df['risk_score'].apply(
        lambda s: 'CRITICAL' if s >= 3 else (
                  'HIGH' if s == 2 else (
                  'MEDIUM' if s == 1 else 'LOW')))
    return df