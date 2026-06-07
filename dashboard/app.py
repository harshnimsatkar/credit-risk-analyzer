import sys
sys.path.append("../src")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import pickle
import plotly.express as px
import plotly.graph_objects as go
import os

# Page config

st.set_page_config(
    page_title="Credit Risk Analyzer",
    page_icon="🛡️",
    layout="wide"
)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Load data

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "risk_scores_full.csv"))
    return df

@st.cache_resource
def load_model():
    with open(os.path.join(BASE_DIR, "models", "lgbm_model.pkl"), "rb") as f:
        model = pickle.load(f)
    return model

df = load_data()
model = load_model()

# Sidebar navigation
st.sidebar.title("Credit Risk Analyzer")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "Overview",
    "Time Analysis",
    "Merchant Risk",
    "Velocity Analysis",
    "Risk Tiers",
    "Risk Scorer"
])


# page 1 - overview

if page == "Overview":
    st.title("Credit Card Fraud Risk — Overview")
    st.markdown("Analysis of **1.85M transactions** using SQL rules + LightGBM (AUC: 0.9849)")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", f"{len(df):,}")
    col2.metric("Fraud Cases", f"{df['is_fraud'].sum():,}")
    col3.metric("Fraud Rate", f"{df['is_fraud'].mean()*100:.3f}%")
    col4.metric("Avg Fraud Amount", f"${df[df['is_fraud']==1]['amt'].mean():.2f}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Class Distribution")
        class_df = df['is_fraud'].value_counts().reset_index()
        class_df.columns = ['label','count']
        class_df['label'] = class_df['label'].map({0:'Legit',1:'Fraud'})
        fig = px.bar(class_df, x='label', y='count',
                     color='label',
                     color_discrete_map={'Legit':'#1976d2','Fraud':'#d32f2f'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("ML Risk Tier Distribution")
        tier_df = df['ml_risk_tier'].value_counts().reset_index()
        tier_df.columns = ['tier','count']
        color_map = {'LOW':'#43a047','MEDIUM':'#ff9800','HIGH':'#d32f2f','CRITICAL':'#b71c1c'}
        fig = px.bar(tier_df, x='tier', y='count',
                     color='tier', color_discrete_map=color_map)
        st.plotly_chart(fig, use_container_width=True)


#part 2 - time analysis
elif page == "Time Analysis":
    st.title("Time-Based Fraud Analysis")
    st.info("Fraud rate spikes 25x during 10pm-3am window")

    conn = sqlite3.connect(os.path.join(BASE_DIR, "data", "credit_risk.db"))
    df_hour = pd.read_sql_query("""
        SELECT
            CAST(strftime('%H', trans_date_trans_time) AS INTEGER) AS hour_of_day,
            COUNT(*) AS total_txns,
            SUM(is_fraud) AS fraud_txns,
            ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_pct
        FROM transactions
        GROUP BY hour_of_day ORDER BY hour_of_day
    """, conn)
    conn.close()

    colors = ['#d32f2f' if p > 1.0 else '#ff9800' if p > 0.15 else '#43a047'
              for p in df_hour['fraud_pct']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_hour['hour_of_day'], y=df_hour['fraud_pct'],
        marker_color=colors, name='Fraud Rate %'
    ))
    fig.add_hline(y=df_hour['fraud_pct'].mean(), line_dash="dash",
                  line_color="orange",
                  annotation_text=f"Avg: {df_hour['fraud_pct'].mean():.3f}%")
    fig.update_layout(title='Fraud Rate % by Hour of Day',
                      xaxis_title='Hour (24hr)', yaxis_title='Fraud Rate (%)')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Peak Fraud Hour", "22:00 (10pm)", "2.601%")
    col2.metric("Safest Hour", "10:00 (10am)", "0.086%")
    col3.metric("Night Window Fraud", "5,689 cases", "58.9% of all fraud")

#page 3 - merchant riskpage

elif page == "Merchant Risk":
    st.title("Merchant Category Risk Analysis")
    st.info("3 categories account for 58% of all fraud cases")

    conn = sqlite3.connect(os.path.join(BASE_DIR, "data", "credit_risk.db"))
    df_merch = pd.read_sql_query("""
        SELECT category,
               COUNT(*) AS total_txns,
               SUM(is_fraud) AS fraud_txns,
               ROUND(SUM(is_fraud)*100.0/COUNT(*),3) AS fraud_pct,
               ROUND(SUM(CASE WHEN is_fraud=1 THEN amt ELSE 0 END),2) AS total_fraud_amt
        FROM transactions
        GROUP BY category ORDER BY fraud_pct DESC
    """, conn)
    conn.close()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df_merch, x='fraud_pct', y='category',
                     orientation='h', color='fraud_pct',
                     color_continuous_scale='RdYlGn_r',
                     title='Fraud Rate % by Category')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(df_merch, x='total_fraud_amt', y='category',
                     orientation='h', color='total_fraud_amt',
                     color_continuous_scale='Blues',
                     title='Total Fraud Loss by Category ($)')
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_merch, use_container_width=True)

# ═════════════════════════════════════════════════════════
# page 4 - velocity analysis

elif page == "Velocity Analysis":
    st.title("Transaction Velocity Analysis")
    st.info("Cards with 5+ transactions in 60 mins are 37x more likely to be fraud")

    vel_data = pd.DataFrame({
        'velocity_flag': ['HIGH VELOCITY','MEDIUM VELOCITY','NORMAL'],
        'fraud_pct':     [15.930, 3.247, 0.427],
        'total_txns':    [973, 43794, 1803631],
        'fraud_txns':    [155, 1422, 7703],
        'avg_amt':       [152.89, 83.79, 69.60]
    })

    col1, col2, col3 = st.columns(3)
    col1.metric("HIGH VELOCITY Fraud Rate", "15.93%", "37x vs Normal")
    col2.metric("MEDIUM VELOCITY Fraud Rate", "3.25%", "8x vs Normal")
    col3.metric("NORMAL Fraud Rate", "0.43%", "baseline")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(vel_data, x='velocity_flag', y='fraud_pct',
                     color='velocity_flag',
                     color_discrete_map={
                         'HIGH VELOCITY':'#d32f2f',
                         'MEDIUM VELOCITY':'#ff9800',
                         'NORMAL':'#43a047'},
                     title='Fraud Rate by Velocity Flag')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(vel_data, x='velocity_flag', y='avg_amt',
                     color='velocity_flag',
                     color_discrete_map={
                         'HIGH VELOCITY':'#d32f2f',
                         'MEDIUM VELOCITY':'#ff9800',
                         'NORMAL':'#43a047'},
                     title='Average Transaction Amount by Velocity')
        st.plotly_chart(fig, use_container_width=True)


# page 5 - risk tiers
elif page == "Risk Tiers":
    st.title("Combined Risk Tier Analysis")
    st.info("4 signals combined: Night hours + Merchant category + Velocity + Amount")

    tier_data = pd.DataFrame({
        'risk_tier': ['CRITICAL','HIGH','MEDIUM','LOW'],
        'total_txns':[4414, 126333, 597889, 1123758],
        'fraud_txns':[2936, 3473,   2811,   431],
        'fraud_pct': [66.516, 2.749, 0.470, 0.038],
        'avg_amt':   [907.61, 142.32, 79.13, 53.83]
    })

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CRITICAL Fraud Rate", "66.5%", "2 in 3 are fraud")
    col2.metric("HIGH Fraud Rate", "2.75%", "5x average")
    col3.metric("MEDIUM Fraud Rate", "0.47%", "near average")
    col4.metric("LOW Fraud Rate", "0.038%", "1750x safer than CRITICAL")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(tier_data, x='risk_tier', y='fraud_pct',
                     color='risk_tier',
                     color_discrete_map={
                         'CRITICAL':'#b71c1c','HIGH':'#d32f2f',
                         'MEDIUM':'#ff9800','LOW':'#43a047'},
                     title='Fraud Rate % by Risk Tier')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(tier_data, x='risk_tier', y='avg_amt',
                     color='risk_tier',
                     color_discrete_map={
                         'CRITICAL':'#b71c1c','HIGH':'#d32f2f',
                         'MEDIUM':'#ff9800','LOW':'#43a047'},
                     title='Average Transaction Amount by Tier')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Tier Breakdown")
    st.dataframe(tier_data, use_container_width=True)


# page 6 — Risk scorer

elif page == "Risk Scorer":
    st.title("Live Transaction Risk Scorer")
    st.markdown("Enter transaction details to get an instant ML risk score")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        amt = st.slider("Transaction Amount ($)", 1.0, 2000.0, 100.0, step=0.5)
        hour = st.slider("Hour of Day (24hr)", 0, 23, 12)
        dayofweek = st.selectbox("Day of Week",
                                  options=[0,1,2,3,4,5,6],
                                  format_func=lambda x: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][x])
        month = st.selectbox("Month", list(range(1,13)),
                              format_func=lambda x: ['Jan','Feb','Mar','Apr','May','Jun',
                                                      'Jul','Aug','Sep','Oct','Nov','Dec'][x-1])

    with col2:
        category = st.selectbox("Merchant Category", [
            'shopping_net','misc_net','grocery_pos','shopping_pos',
            'gas_transport','misc_pos','grocery_net','travel',
            'personal_care','entertainment','kids_pets','food_dining',
            'home','health_fitness'
        ])
        velocity = st.selectbox("Transaction Velocity",
                                 options=[0,1,2],
                                 format_func=lambda x: {0:'Normal',1:'Medium (3 txns/hr)',2:'High (5+ txns/hr)'}[x])

    # Compute features
    is_night = 1 if (hour <= 3 or hour >= 22) else 0
    is_high_risk_merchant = 1 if category in ['shopping_net','misc_net','grocery_pos'] else 0
    is_high_amount = 1 if amt > 500 else 0
    rule_risk_score = is_night + is_high_risk_merchant + (1 if velocity==2 else 0) + is_high_amount

    input_df = pd.DataFrame([{
        'amt': amt, 'hour': hour, 'dayofweek': dayofweek,
        'month': month, 'is_night': is_night,
        'is_high_risk_merchant': is_high_risk_merchant,
        'is_high_amount': is_high_amount,
        'velocity_flag': velocity,
        'risk_score': rule_risk_score
    }])

    ml_score = model.predict_proba(input_df)[0][1] * 100

    if ml_score >= 60:
        tier = "CRITICAL"
        color = "#b71c1c"
        action = "BLOCK — Automatic hold, manual review required"
    elif ml_score >= 30:
        tier = "HIGH"
        color = "#d32f2f"
        action = "STEP-UP AUTH — Trigger OTP / biometric verification"
    elif ml_score >= 10:
        tier = "MEDIUM"
        color = "#ff9800"
        action = "MONITOR — Flag for batch review"
    else:
        tier = "LOW"
        color = "#43a047"
        action = "PASS — No friction added"

    st.markdown("---")
    st.subheader("Risk Assessment Result")

    col1, col2, col3 = st.columns(3)
    col1.metric("ML Risk Score", f"{ml_score:.1f} / 100")
    col2.metric("Risk Tier", tier)
    col3.metric("Rule Score", f"{rule_risk_score} / 4 signals")

    st.markdown(f"**Recommended Action:** {action}")

    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ml_score,
        title={'text': "Fraud Risk Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 10],  'color': '#e8f5e9'},
                {'range': [10, 30], 'color': '#fff8e1'},
                {'range': [30, 60], 'color': '#ffebee'},
                {'range': [60, 100],'color': '#ffcdd2'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': ml_score
            }
        }
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Signal Breakdown")
    signals = pd.DataFrame({
        'Signal': ['Night Hour (10pm-3am)', 'High Risk Merchant',
                   'High Velocity (5+ txns/hr)', 'High Amount (>$500)'],
        'Triggered': ['Yes' if is_night else 'No',
                      'Yes' if is_high_risk_merchant else 'No',
                      'Yes' if velocity==2 else 'No',
                      'Yes' if is_high_amount else 'No']
    })
    st.dataframe(signals, use_container_width=True, hide_index=True)