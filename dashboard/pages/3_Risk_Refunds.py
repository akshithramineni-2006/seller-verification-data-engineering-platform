
import pandas as pd
import streamlit as st

from dashboard.common import (
    AMBER,
    CORAL,
    TAUPE,
    WALNUT,
    format_inr,
    inject_styles,
    load_csv,
    page_header,
    require_data,
    show_kpi,
)

st.set_page_config(
    page_title="Risk & Refunds",
    page_icon="🛡️",
    layout="wide",
)

inject_styles()

page_header(
    "Risk & Refunds",
    "Identify high-risk sellers and compare refund performance across business types.",
)

risk_df = load_csv("high_risk_sellers.csv")
risk_distribution_df = load_csv("risk_score_distribution.csv")
overall_metrics_df = load_csv("overall_risk_metrics.csv")
refund_df = load_csv("refund_rate.csv")
business_df = load_csv("revenue_by_business.csv")

require_data(
    ("High-risk sellers", risk_df),
    ("Risk score distribution", risk_distribution_df),
    ("Overall risk metrics", overall_metrics_df),
    ("Refund rates", refund_df),
    ("Revenue by business type", business_df),
)
# Validate the columns required by this page
if "risk_score" not in risk_df.columns:
    st.error("The high-risk sellers export does not contain risk_score.")
    st.stop()
if not {"risk_band", "seller_count"}.issubset(
    risk_distribution_df.columns
):
    st.error("The risk distribution export is missing required columns.")
    st.stop()
if not {"business_type", "refund_percentage"}.issubset(refund_df.columns):
    st.error("The refund export is missing required columns.")
    st.stop()

if not {"business_type", "total_sales"}.issubset(business_df.columns):
    st.error("The business revenue export is missing required columns.")
    st.stop()

risk_df = risk_df.copy()
refund_df = refund_df.copy()
business_df = business_df.copy()

risk_df["risk_score"] = pd.to_numeric(
    risk_df["risk_score"], errors="coerce"
)

refund_df["refund_percentage"] = pd.to_numeric(
    refund_df["refund_percentage"], errors="coerce"
).fillna(0)

business_df["total_sales"] = pd.to_numeric(
    business_df["total_sales"], errors="coerce"
).fillna(0)


# Overall risk metrics from the full seller warehouse
if overall_metrics_df.empty:
    st.error("The overall risk metrics export contains no data.")
    st.stop()

metrics = overall_metrics_df.iloc[0]

average_risk = float(metrics["average_risk_score"])
maximum_risk = float(metrics["maximum_risk_score"])
high_risk_count = int(metrics["high_risk_sellers"])

average_refund = (
    float(refund_df["refund_percentage"].mean())
    if not refund_df.empty
    else 0
)

kpis = st.columns(4)

show_kpi(
    kpis[0], "High-Risk Sellers", f"{high_risk_count:,}", CORAL
)
show_kpi(
    kpis[1], "Average Risk Score", f"{average_risk:.2f}", TAUPE
)
show_kpi(
    kpis[2], "Maximum Risk Score", f"{maximum_risk:.0f}", WALNUT
)
show_kpi(
    kpis[3], "Average Refund Rate", f"{average_refund:.2f}%", AMBER
)

st.divider()

# High-risk sellers


st.subheader("Risk Score Distribution")
st.caption(
    "Distribution across all sellers in the warehouse. "
    "Higher scores indicate higher recorded risk."
)

risk_distribution_df = risk_distribution_df.copy()
risk_distribution_df["seller_count"] = pd.to_numeric(
    risk_distribution_df["seller_count"],
    errors="coerce",
).fillna(0)

st.bar_chart(
    risk_distribution_df,
    x="risk_band",
    y="seller_count",
    color=CORAL,
)

st.dataframe(
    risk_distribution_df.rename(
        columns={
            "risk_band": "Risk Band",
            "seller_count": "Seller Count",
        }
    ),
    width="stretch",
    hide_index=True,
)


st.divider()

st.subheader("Top 10 High-Risk Sellers")
st.caption(
    "Individual sellers ranked by risk score. "
    "Tied scores are valid and do not imply a ranking difference."
)

top_risk = risk_df.sort_values(
    ["risk_score", "seller_id"],
    ascending=[False, True],
).head(10)

st.dataframe(
    top_risk,
    width="stretch",
    hide_index=True,
)
st.divider()

# Refund rates
st.subheader("Refund Rate by Business Type")
st.caption("Refund percentages are rates, not monetary amounts.")

refund_sorted = refund_df.sort_values(
    "refund_percentage", ascending=True
)

st.bar_chart(
    refund_sorted,
    x="business_type",
    y="refund_percentage",
    color=TAUPE,
    horizontal=True,
)

st.dataframe(
    refund_sorted,
    width="stretch",
    hide_index=True,
)

st.divider()

# Revenue and refunds comparison
st.subheader("Revenue and Refund Comparison")
st.caption(
    "Compare business sales in Indian Rupees with refund performance."
)

comparison = business_df.merge(
    refund_df[
        ["business_type", "refund_percentage"]
    ],
    on="business_type",
    how="left",
)

comparison["Revenue (₹ INR)"] = comparison["total_sales"].map(format_inr)
comparison["Refund Rate"] = comparison["refund_percentage"].map(
    lambda value: f"{value:.2f}%" if pd.notna(value) else "N/A"
)

comparison = comparison.sort_values(
    "total_sales", ascending=False
)

st.bar_chart(
    comparison,
    x="business_type",
    y="total_sales",
    color=WALNUT,
    horizontal=True,
)

st.dataframe(
    comparison.drop(columns=["total_sales", "refund_percentage"]),
    width="stretch",
    hide_index=True,
)

st.caption(
    "Revenue is displayed in ₹ INR. Risk scores and refund percentages "
    "retain their original units. Source exports remain unchanged."
)
