import streamlit as st
import pandas as pd
import requests

# ================== CONFIG ==================
API_URL = "http://127.0.0.1:8000/orders"

st.set_page_config(
    page_title="Smart Delivery Analytics Dashboard",
    layout="wide"
)

# ================== SESSION ==================
if "auth" not in st.session_state:
    st.session_state.auth = True

# ================== HEADER ==================
st.title("📊 Smart Delivery Analytics Dashboard")

col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Logout"):
        st.session_state.auth = False
        st.stop()

# ================== FETCH DATA ==================
try:
    data = requests.get(API_URL, timeout=5).json()
except Exception:
    st.error("Backend API is not running")
    st.stop()

if not data:
    st.warning("No data available yet.")
    st.stop()

df = pd.DataFrame(
    data,
    columns=[
        "order_id", "latitude", "longitude", "weight",
        "priority", "vehicle", "distance_km",
        "delivery_cost", "created_at"
    ]
)

df["created_at"] = pd.to_datetime(df["created_at"])
df["date"] = df["created_at"].dt.date
df["cost_per_km"] = df["delivery_cost"] / df["distance_km"]

# ================== SIDEBAR FILTERS ==================
st.sidebar.header("🔎 Filters")

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    options=df["vehicle"].unique(),
    default=df["vehicle"].unique()
)

priority_filter = st.sidebar.multiselect(
    "Priority",
    options=df["priority"].unique(),
    default=df["priority"].unique()
)

date_range = st.sidebar.date_input(
    "Date Range",
    [df["date"].min(), df["date"].max()]
)

filtered_df = df[
    (df["vehicle"].isin(vehicle_filter)) &
    (df["priority"].isin(priority_filter)) &
    (df["date"] >= date_range[0]) &
    (df["date"] <= date_range[1])
]

# ================== KPIs ==================
st.markdown("## 📌 Key Metrics")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders", len(filtered_df))
k2.metric("Total Cost (₹)", round(filtered_df["delivery_cost"].sum(), 2))
k3.metric("Avg Cost / Order (₹)", round(filtered_df["delivery_cost"].mean(), 2))
k4.metric("Avg Cost / Km (₹)", round(filtered_df["cost_per_km"].mean(), 2))

st.divider()

# ================== TABS ==================
tab1, tab2, tab3 = st.tabs(
    ["📈 Trends", "🧠 Analytics", "📦 Orders"]
)

# ================== TAB 1: TRENDS ==================
with tab1:
    st.subheader("📊 Order Distribution by Vehicle")

    vehicle_orders = (
        filtered_df.groupby("vehicle")
        .size()
        .reset_index(name="orders")
    )

    st.bar_chart(vehicle_orders, x="vehicle", y="orders")

    st.subheader("💰 Cost Contribution by Vehicle (%)")

    vehicle_cost = (
        filtered_df.groupby("vehicle")["delivery_cost"]
        .sum()
        .reset_index()
    )

    vehicle_cost["cost_pct"] = (
        vehicle_cost["delivery_cost"]
        / vehicle_cost["delivery_cost"].sum()
    ) * 100

    st.bar_chart(vehicle_cost, x="vehicle", y="cost_pct")


# ================== TAB 2: NLP ANALYTICS ==================
with tab2:
    st.subheader("🧠 Ask Analytical Questions")

    query = st.text_input(
        "Examples: most expensive order | average cost | vehicle performance"
    ).lower()

    if not query:
        st.info("Enter a query above.")
    elif "most expensive" in query:
        row = filtered_df.loc[filtered_df["delivery_cost"].idxmax()]
        st.success(
            f"Order {row['order_id']} with cost ₹{row['delivery_cost']}"
        )
    elif "average cost" in query:
        st.success(
            f"Average delivery cost: ₹{round(filtered_df['delivery_cost'].mean(), 2)}"
        )
    elif "vehicle performance" in query:
        st.success(
            filtered_df.groupby("vehicle")["delivery_cost"].mean().to_string()
        )
    else:
        st.warning("Query not supported yet.")

# ================== TAB 3: ORDERS + EXPORT ==================
with tab3:
    st.subheader("📦 Filtered Orders")

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        data=csv,
        file_name="delivery_analysis.csv",
        mime="text/csv"
    )
