import pandas as pd

def preprocess_transactions(df):
    df = df.copy()
    df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
    df['hour']      = df['trans_date_trans_time'].dt.hour
    df['dayofweek'] = df['trans_date_trans_time'].dt.dayofweek
    df['month']     = df['trans_date_trans_time'].dt.month
    df['is_night']  = df['hour'].apply(lambda h: 1 if (h<=3 or h>=22) else 0)
    df['is_high_risk_merchant'] = df['category'].apply(
        lambda c: 1 if c in ['shopping_net','misc_net','grocery_pos'] else 0)
    df['is_high_amount'] = (df['amt'] > 500).astype(int)
    return df

def preprocess_creditcard(df):
    df = df.copy()
    df['is_high_amount'] = (df['Amount'] > 500).astype(int)
    return df