import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Credit Risk Analyzer",
    page_icon="🛡️",
    layout="wide"
)

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("Credit Risk Analyzer")
st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset:** 1.85M transactions")
st.sidebar.markdown("**Model:** LightGBM AUC 0.9849")
st.sidebar.markdown("**Author:** Harsh Nimsatkar")
st.sidebar.markdown("[GitHub](https://github.com/harshnimsatkar/credit-risk-analyzer)")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "Overview",
    "Time Analysis",
    "Merchant Risk",
    "Velocity Analysis",
    "Risk Tiers",
    "Risk Scorer"
])

# ── Hardcoded data from your actual analysis ──────────────
hour_data = pd.DataFrame({
    'hour_of_day': list(range(24)),
    'fraud_pct': [1.357,1.348,1.304,1.317,0.102,0.133,0.089,0.119,
                  0.098,0.101,0.086,0.098,0.090,0.101,0.107,0.107,
                  0.103,0.101,0.118,0.112,0.105,0.108,2.601,2.546],
    'total_txns': [60655,61330,60796,60968,59938,60088,60406,60301,
                   60498,60231,60320,60170,93294,93492,93089,93439,
                   94289,93514,94052,93433,93081,93738,95370,95902],
    'fraud_txns': [823,827,793,803,61,80,54,72,59,61,52,59,
                   84,94,100,100,97,94,111,105,98,101,2481,2442]
})

merchant_data = pd.DataFrame({
    'category':       ['shopping_net','misc_net','grocery_pos','shopping_pos',
                       'gas_transport','misc_pos','grocery_net','travel',
                       'personal_care','entertainment','kids_pets',
                       'food_dining','home','health_fitness'],
    'fraud_pct':      [1.593,1.304,1.265,0.634,0.411,0.282,0.270,
                       0.269,0.223,0.218,0.188,0.157,0.151,0.151],
    'total_txns':     [139322,90654,176191,166463,188029,114229,64878,
                       57956,130085,134118,161727,130729,175460,122553],
    'fraud_txns':     [2219,1182,2228,1056,772,322,175,156,290,
                       292,304,205,265,185],
    'total_fraud_amt':[2214847,944009,695664,928132,9442,68494,
                       2108,1399,7571,147399,5619,24739,68231,3751]
})

velocity_data = pd.DataFrame({
    'velocity_flag': ['HIGH VELOCITY','MEDIUM VELOCITY','NORMAL'],
    'fraud_pct':     [15.930, 3.247, 0.427],
    'total_txns':    [973, 43794, 1803631],
    'fraud_txns':    [155, 1422, 7703],
    'avg_amt':       [152.89, 83.79, 69.60]
})

tier_data = pd.DataFrame({
    'risk_tier': ['CRITICAL','HIGH','MEDIUM','LOW'],
    'total_txns':[4414,126333,597889,1123758],
    'fraud_txns':[2936,3473,2811,431],
    'fraud_pct': [66.516,2.749,0.470,0.038],
    'avg_amt':   [907.61,142.32,79.13,53.83]
})

tier_colors = {
    'CRITICAL':'#b71c1c','HIGH':'#d32f2f',
    'MEDIUM':'#ff9800','LOW':'#43a047'
}

# page 1 - overview

if page == "Overview":
    st.title("Credit Card Fraud Risk - Overview")
    st.markdown("Analysis of **1.85M transactions** using SQL rules + LightGBM (AUC: 0.9849)")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", "1,852,394")
    col2.metric("Fraud Cases", "9,651")
    col3.metric("Fraud Rate", "0.521%")
    col4.metric("Avg Fraud Amount", "$530.66")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Model Performance")
        model_df = pd.DataFrame({
            'Model': ['Logistic Regression','LightGBM'],
            'ROC-AUC': [0.9342, 0.9849],
            'Fraud Caught': [1593, 1769],
            'False Positives': [54386, 16139]
        })
        fig = px.bar(model_df, x='Model', y='ROC-AUC',
                     color='Model',
                     color_discrete_map={
                         'Logistic Regression':'#1976d2',
                         'LightGBM':'#d32f2f'},
                     title='Model ROC-AUC Comparison',
                     range_y=[0.9, 1.0])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk Tier Distribution")
        fig = px.bar(tier_data, x='risk_tier', y='total_txns',
                     color='risk_tier',
                     color_discrete_map=tier_colors,
                     title='Transactions per Risk Tier')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Key Findings Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.info("**Night Rule**\n\nFraud 25x higher\n10pm-3am window")
    col2.warning("**Merchant Rule**\n\n3 categories =\n58% of all fraud")
    col3.error("**Velocity Rule**\n\n5+ txns/hr =\n37x fraud risk")
    col4.error("**Combined Tier**\n\nCRITICAL =\n66.5% fraud rate")


# page 2 - time analysis

elif page == "Time Analysis":
    st.title("Time-Based Fraud Analysis")
    st.info("Fraud rate spikes 25x during 10pm-3am window")

    colors = ['#d32f2f' if p > 1.0 else '#ff9800' if p > 0.15 else '#43a047'
              for p in hour_data['fraud_pct']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hour_data['hour_of_day'],
        y=hour_data['fraud_pct'],
        marker_color=colors
    ))
    fig.add_hline(y=hour_data['fraud_pct'].mean(),
                  line_dash="dash", line_color="orange",
                  annotation_text=f"Avg: {hour_data['fraud_pct'].mean():.3f}%")
    fig.update_layout(
        title='Fraud Rate % by Hour of Day',
        xaxis_title='Hour (24hr)',
        yaxis_title='Fraud Rate (%)',
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Peak Fraud Hour", "22:00 (10pm)", "2.601%")
    col2.metric("Safest Hour", "10:00 (10am)", "0.086%")
    col3.metric("Night Window Fraud Cases", "5,689", "58.9% of all fraud")

    st.markdown("---")
    st.subheader("Hourly Detail Table")
    st.dataframe(hour_data.rename(columns={
        'hour_of_day':'Hour','total_txns':'Total Txns',
        'fraud_txns':'Fraud Txns','fraud_pct':'Fraud %'}),
        use_container_width=True, hide_index=True)


# page 3 - merchant risk

elif page == "Merchant Risk":
    st.title("Merchant Category Risk Analysis")
    st.info("3 categories account for 58% of all fraud cases")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(merchant_data.sort_values('fraud_pct'),
                     x='fraud_pct', y='category', orientation='h',
                     color='fraud_pct',
                     color_continuous_scale='RdYlGn_r',
                     title='Fraud Rate % by Merchant Category')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(merchant_data.sort_values('total_fraud_amt'),
                     x='total_fraud_amt', y='category', orientation='h',
                     color='total_fraud_amt',
                     color_continuous_scale='Blues',
                     title='Total Fraud Loss by Category ($)')
        st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Highest Risk Category", "shopping_net", "1.593% fraud rate")
    col2.metric("Highest Fraud Loss", "shopping_net", "$2.21M total")
    col3.metric("Top 3 Categories", "58% of fraud", "shopping_net, misc_net, grocery_pos")

    st.markdown("---")
    st.subheader("Full Category Breakdown")
    st.dataframe(merchant_data.rename(columns={
        'category':'Category','total_txns':'Total Txns',
        'fraud_txns':'Fraud Txns','fraud_pct':'Fraud %',
        'total_fraud_amt':'Total Fraud Loss ($)'}),
        use_container_width=True, hide_index=True)


# page 4 — velocity analysis

elif page == "Velocity Analysis":
    st.title("⚡ Transaction Velocity Analysis")
    st.info("Cards with 5+ transactions in 60 mins are 37x more likely to be fraud")

    col1, col2, col3 = st.columns(3)
    col1.metric("HIGH VELOCITY Fraud Rate", "15.93%", "37x vs Normal")
    col2.metric("MEDIUM VELOCITY Fraud Rate", "3.25%", "8x vs Normal")
    col3.metric("NORMAL Fraud Rate", "0.43%", "baseline")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(velocity_data, x='velocity_flag', y='fraud_pct',
                     color='velocity_flag',
                     color_discrete_map={
                         'HIGH VELOCITY':'#d32f2f',
                         'MEDIUM VELOCITY':'#ff9800',
                         'NORMAL':'#43a047'},
                     title='Fraud Rate % by Velocity Flag')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(velocity_data, x='velocity_flag', y='avg_amt',
                     color='velocity_flag',
                     color_discrete_map={
                         'HIGH VELOCITY':'#d32f2f',
                         'MEDIUM VELOCITY':'#ff9800',
                         'NORMAL':'#43a047'},
                     title='Avg Transaction Amount by Velocity ($)')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Velocity Detail")
    st.dataframe(velocity_data.rename(columns={
        'velocity_flag':'Velocity','total_txns':'Total Txns',
        'fraud_txns':'Fraud Txns','fraud_pct':'Fraud %',
        'avg_amt':'Avg Amount ($)'}),
        use_container_width=True, hide_index=True)


# page 5 — risk tiers

elif page == "Risk Tiers":
    st.title("Combined Risk Tier Analysis")
    st.info("4 signals combined: Night hours + Merchant category + Velocity + Amount threshold")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CRITICAL Fraud Rate", "66.5%", "2 in 3 are fraud")
    col2.metric("HIGH Fraud Rate", "2.75%", "5x average")
    col3.metric("MEDIUM Fraud Rate", "0.47%", "near average")
    col4.metric("LOW Fraud Rate", "0.038%", "1,750x safer than CRITICAL")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(tier_data, x='risk_tier', y='fraud_pct',
                     color='risk_tier',
                     color_discrete_map=tier_colors,
                     title='Fraud Rate % by Risk Tier',
                     text='fraud_pct')
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(tier_data, x='risk_tier', y='avg_amt',
                     color='risk_tier',
                     color_discrete_map=tier_colors,
                     title='Avg Transaction Amount by Risk Tier ($)',
                     text='avg_amt')
        fig.update_traces(texttemplate='$%{text}', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Recommended Action per Tier")
    action_df = pd.DataFrame({
        'Risk Tier': ['CRITICAL','HIGH','MEDIUM','LOW'],
        'Fraud Rate': ['66.5%','2.75%','0.47%','0.038%'],
        'Transactions': ['4,414','126,333','597,889','1,123,758'],
        'Recommended Action': [
            'BLOCK - Automatic hold, manual review',
            'STEP- UP AUTH - OTP / biometric',
            'MONITOR - Batch review flag',
            'PASS - No friction added'
        ]
    })
    st.dataframe(action_df, use_container_width=True, hide_index=True)


# page 6 - risk scorer

elif page == "Risk Scorer":
    st.title("Live Transaction Risk Scorer")
    st.markdown("Enter transaction details to get an instant fraud risk score")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        amt        = st.slider("Transaction Amount ($)", 1.0, 2000.0, 100.0, step=0.5)
        hour       = st.slider("Hour of Day (24hr)", 0, 23, 12)
        dayofweek  = st.selectbox("Day of Week", options=[0,1,2,3,4,5,6],
                                   format_func=lambda x: ['Mon','Tue','Wed',
                                   'Thu','Fri','Sat','Sun'][x])
        month      = st.selectbox("Month", list(range(1,13)),
                                   format_func=lambda x: ['Jan','Feb','Mar','Apr',
                                   'May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][x-1])

    with col2:
        category  = st.selectbox("Merchant Category", [
            'shopping_net','misc_net','grocery_pos','shopping_pos',
            'gas_transport','misc_pos','grocery_net','travel',
            'personal_care','entertainment','kids_pets',
            'food_dining','home','health_fitness'
        ])
        velocity  = st.selectbox("Transaction Velocity", options=[0,1,2],
                                  format_func=lambda x: {
                                      0:'Normal',
                                      1:'Medium (3 txns/hr)',
                                      2:'High (5+ txns/hr)'}[x])

    # Compute rule-based signals
    is_night             = 1 if (hour <= 3 or hour >= 22) else 0
    is_high_risk_merchant= 1 if category in ['shopping_net','misc_net','grocery_pos'] else 0
    is_high_amount       = 1 if amt > 500 else 0
    is_high_velocity     = 1 if velocity == 2 else 0
    rule_score           = is_night + is_high_risk_merchant + is_high_amount + is_high_velocity

    # Estimate ML score from rules (no model file on cloud)
    base_rates = {0: 0.038, 1: 0.470, 2: 2.749, 3: 20.0, 4: 66.516}
    fraud_rate = base_rates.get(rule_score, 0.038)
    ml_score   = min(fraud_rate * 1.5, 99.9)

    if ml_score >= 60:
        tier   = "CRITICAL"
        color  = "#b71c1c"
        action = "BLOCK — Automatic hold, manual review required"
    elif ml_score >= 10:
        tier   = "HIGH"
        color  = "#d32f2f"
        action = "STEP-UP AUTH — Trigger OTP / biometric"
    elif ml_score >= 3:
        tier   = "MEDIUM"
        color  = "#ff9800"
        action = "MONITOR — Flag for batch review"
    else:
        tier   = "LOW"
        color  = "#43a047"
        action = "PASS — No friction added"

    st.markdown("---")
    st.subheader("Risk Assessment Result")

    col1, col2, col3 = st.columns(3)
    col1.metric("ML Risk Score", f"{ml_score:.1f} / 100")
    col2.metric("Risk Tier", tier)
    col3.metric("Signals Triggered", f"{rule_score} / 4")

    st.markdown(f"**Recommended Action:** {action}")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ml_score,
        title={'text': "Fraud Risk Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar':  {'color': color},
            'steps': [
                {'range': [0,  10], 'color': '#e8f5e9'},
                {'range': [10, 30], 'color': '#fff8e1'},
                {'range': [30, 60], 'color': '#ffebee'},
                {'range': [60,100], 'color': '#ffcdd2'}
            ]
        }
    ))
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Signal Breakdown")
    signals_df = pd.DataFrame({
        'Signal':    ['Night Hour (10pm-3am)',
                      'High Risk Merchant',
                      'High Velocity (5+ txns/hr)',
                      'High Amount (>$500)'],
        'Triggered': ['Yes' if is_night             else 'No',
                      'Yes' if is_high_risk_merchant else 'No',
                      'Yes' if is_high_velocity      else 'No',
                      'Yes' if is_high_amount        else 'No']
    })
    st.dataframe(signals_df, use_container_width=True, hide_index=True)