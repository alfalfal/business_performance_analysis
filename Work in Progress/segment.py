import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide")
st.title("📊 Customer Segmentation Dashboard")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_data/customers.csv")
    
    # Convert dates safely
    for col in ['first_order_date', 'last_order_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

df = load_data()

# -------------------------
# VALIDATION
# -------------------------
required_cols = ['customer_segment', 'value_score', 'risk_score', 'gmv_delivered']

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("Filters")

segments = st.sidebar.multiselect(
    "Customer Segment",
    options=df['customer_segment'].dropna().unique(),
    default=df['customer_segment'].dropna().unique()
)

states = st.sidebar.multiselect(
    "State",
    options=df['customer_state'].dropna().unique() if 'customer_state' in df.columns else [],
    default=df['customer_state'].dropna().unique() if 'customer_state' in df.columns else []
)

df_filtered = df.copy()

if 'customer_segment' in df.columns:
    df_filtered = df_filtered[df_filtered['customer_segment'].isin(segments)]

if 'customer_state' in df.columns:
    df_filtered = df_filtered[df_filtered['customer_state'].isin(states)]

# -------------------------
# KPIs
# -------------------------
st.subheader("📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Customers", len(df_filtered))
col2.metric("Avg Value Score", round(df_filtered['value_score'].mean(), 2))
col3.metric("Avg Risk Score", round(df_filtered['risk_score'].mean(), 2))
col4.metric("Total GMV", round(df_filtered['gmv_delivered'].sum(), 0))

# -------------------------
# CHARTS
# -------------------------
st.subheader("📊 Insights")

col1, col2 = st.columns(2)

# --- Segment Distribution ---
with col1:
    st.markdown("### Customer Segments")
    fig1, ax1 = plt.subplots()
    df_filtered['customer_segment'].value_counts().plot(kind='bar', ax=ax1)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

# --- Action Type (optional) ---
with col2:
    st.markdown("### Action Types")
    
    if 'action_type' in df.columns:
        fig2, ax2 = plt.subplots()
        df_filtered['action_type'].value_counts().head(10).plot(kind='bar', ax=ax2)
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    else:
        st.info("No action_type column found")

# -------------------------
# VALUE vs RISK SCATTER
# -------------------------
st.subheader("🔥 Value vs Risk Matrix")

fig3, ax3 = plt.subplots()

ax3.scatter(
    df_filtered['value_score'],
    df_filtered['risk_score']
)

ax3.set_xlabel("Value Score")
ax3.set_ylabel("Risk Score")

# líneas de decisión
ax3.axhline(y=0.5)
ax3.axvline(x=0.5)

st.pyplot(fig3)

# -------------------------
# TABLE
# -------------------------
st.subheader("📋 Customer Data")

st.dataframe(df_filtered.head(100))