import pandas as pd
import streamlit as st
import plotly.express as px

# LOAD DATA
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_data/customers.csv", parse_dates=["first_order_date", "last_order_date"])

df = load_data()

st.set_page_config(layout="wide")

st.title("Customer Analytics Dashboard")

# SIDEBAR FILTERS
st.sidebar.header("Filters")

segment_filter = st.sidebar.multiselect(
    "Customer Segment",
    options=df["customer_segment"].unique(),
    default=df["customer_segment"].unique()
)

state_filter = st.sidebar.multiselect(
    "State",
    options=df["customer_state"].unique(),
    default=df["customer_state"].unique()
)

filtered_df = df[
    (df["customer_segment"].isin(segment_filter)) &
    (df["customer_state"].isin(state_filter))
]

# KPI METRICS
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", f"{filtered_df.shape[0]:,}")
col2.metric("Total GMV", f"{filtered_df['gmv_delivered'].sum():,.0f}")
col3.metric("Avg Risk Score", f"{filtered_df['risk_score'].mean():.2f}")
col4.metric("Avg Value Score", f"{filtered_df['value_score'].mean():.2f}")

st.divider()

# SEGMENT DISTRIBUTION
col1, col2 = st.columns(2)

with col1:
    fig_seg = px.bar(
        filtered_df.groupby("customer_segment").size().reset_index(name="count"),
        x="customer_segment",
        y="count",
        title="Customer Segments Distribution"
    )
    st.plotly_chart(fig_seg, use_container_width=True)

with col2:
    fig_gmv_seg = px.bar(
        filtered_df.groupby("customer_segment")["gmv_delivered"].sum().reset_index(),
        x="customer_segment",
        y="gmv_delivered",
        title="GMV by Segment"
    )
    st.plotly_chart(fig_gmv_seg, use_container_width=True)

st.divider()

# RISK VS VALUE
fig_scatter = px.scatter(
    filtered_df,
    x="risk_score",
    y="value_score",
    color="customer_segment",
    title="Risk vs Value",
    hover_data=["customer_unique_id"]
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# RECENCY DISTRIBUTION
col1, col2 = st.columns(2)

with col1:
    fig_recency = px.histogram(
        filtered_df,
        x="recency_days",
        nbins=50,
        title="Recency Distribution"
    )
    st.plotly_chart(fig_recency, use_container_width=True)

with col2:
    fig_lifetime = px.histogram(
        filtered_df,
        x="lifetime_days",
        nbins=50,
        title="Lifetime Distribution"
    )
    st.plotly_chart(fig_lifetime, use_container_width=True)

st.divider()

# TOP CUSTOMERS
st.subheader("Top Customers by GMV")

top_customers = filtered_df.sort_values("gmv_delivered", ascending=False).head(20)

st.dataframe(top_customers[[
    "customer_unique_id",
    "customer_segment",
    "gmv_delivered",
    "risk_score",
    "value_score"
]])

st.divider()

# GEOGRAPHICAL DISTRIBUTION
fig_geo = px.bar(
    filtered_df.groupby("customer_state")["customer_unique_id"].count().reset_index(),
    x="customer_state",
    y="customer_unique_id",
    title="Customers by State"
)
st.plotly_chart(fig_geo, use_container_width=True)

st.divider()

# ORDERS VS GMV
fig_orders = px.scatter(
    filtered_df,
    x="n_orders",
    y="gmv_delivered",
    color="customer_segment",
    title="Orders vs GMV"
)
st.plotly_chart(fig_orders, use_container_width=True)

st.divider()

st.caption("Dashboard built for customer segmentation and behavior analysis")