
from pathlib import Path

import pandas as pd
import streamlit as st
from dashboard.common import format_inr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = PROJECT_ROOT / "dashboard" / "exports"

st.set_page_config(
    page_title="Seller Verification Intelligence",
    page_icon="ðŸ“Š",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Amber Walnut palette
WALNUT = "#674D3C"
AMBER = "#D9AD7C"
TAUPE = "#A2836E"
PEACH = "#F9CCAC"
CORAL = "#F4A688"
INK = "#3F3028"
MUTED = "#76665A"
PANEL = "#FFFFFF"
BORDER = "#E5D9CD"


def inject_styles():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #FAF7F3;
            color: {INK};
        }}
        [data-testid="stSidebar"] {{
            background-color: #F3ECE5;
            border-right: 1px solid {BORDER};
        }}
        .hero {{
            padding: 1.4rem 1.6rem;
            background: {PANEL};
            border: 1px solid {BORDER};
            border-left: 6px solid {WALNUT};
            border-radius: 12px;
            margin-bottom: 1.2rem;
        }}
        .hero h1 {{
            color: {WALNUT};
            margin: 0;
            font-size: 2rem;
        }}
        .hero p {{
            color: {MUTED};
            margin: .45rem 0 0 0;
        }}
        .kpi-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-top: 4px solid {AMBER};
            border-radius: 10px;
            padding: 1rem;
            min-height: 110px;
        }}
        .kpi-label {{
            color: {MUTED};
            font-size: .85rem;
        }}
        .kpi-value {{
            color: {WALNUT};
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: .25rem;
        }}
        .section-note {{
            color: {MUTED};
            font-size: .9rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_csv(filename):
    path = EXPORT_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path)


def show_kpi(container, label, value, accent=AMBER):
    container.markdown(
        f"""
        <div class="kpi-card" style="border-top-color:{accent}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

st.sidebar.title("Seller Intelligence")
st.sidebar.caption("Business Intelligence Platform")
st.sidebar.divider()
st.sidebar.info(
    "Choose a page above to explore revenue, verification, risk, "
    "registration trends, and data quality."
)

st.markdown(
    """
    <div class="hero">
        <h1>Executive Overview</h1>
        <p>A concise view of seller performance, verification health, and data quality.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load generated analytics
total_df = load_csv("total_sellers.csv")
country_df = load_csv("revenue_by_country.csv")
verification_df = load_csv("verification_status.csv")
monthly_df = load_csv("monthly_registrations.csv")
quality_df = load_csv("quality_report.csv")
business_df = load_csv("revenue_by_business.csv")

required = {
    "Total sellers": total_df,
    "Revenue by country": country_df,
    "Verification status": verification_df,
    "Monthly registrations": monthly_df,
    "Data quality": quality_df,
    "Revenue by business": business_df,
}

missing = [name for name, data in required.items() if data is None]

if missing:
    st.error("Required exports are missing. Run the pipeline first.")
    st.write("Missing data:", missing)
    st.stop()

total_sellers = int(total_df.iloc[0]["total_sellers"])
approved = int(
    verification_df.loc[
        verification_df["verification_status"] == "Approved",
        "seller_count",
    ].sum()
)
pending = int(
    verification_df.loc[
        verification_df["verification_status"] == "Pending",
        "seller_count",
    ].sum()
)
rejected = int(
    verification_df.loc[
        verification_df["verification_status"] == "Rejected",
        "seller_count",
    ].sum()
)
quality_issues = int(quality_df["Count"].sum())

approval_rate = approved / total_sellers * 100 if total_sellers else 0
selected_revenue = float(country_df["total_sales"].sum())

st.subheader("Business at a glance")

kpis = st.columns(4)
show_kpi(kpis[0], "Total Sellers", f"{total_sellers:,}", WALNUT)
show_kpi(kpis[1], "Total Sales", format_inr(selected_revenue), AMBER)
show_kpi(kpis[2], "Approval Rate", f"{approval_rate:.1f}%", TAUPE)
show_kpi(kpis[3], "Quality Issues", f"{quality_issues:,}", CORAL)

st.write("")

left, right = st.columns(2)

with left:
    st.subheader("Revenue by Country")
    st.caption("Total sales by country (₹ INR).")

    country_chart = country_df.sort_values(
        "total_sales", ascending=True
    ).copy()

    country_chart["Revenue (₹ INR)"] = country_chart["total_sales"].map(
        format_inr
    )

    st.bar_chart(
        country_chart,
        x="country_name",
        y="total_sales",
        color=AMBER,
        horizontal=True,
    )

    st.dataframe(
        country_chart[["country_name", "Revenue (₹ INR)"]],
        width="stretch",
        hide_index=True,
    )
    
with right:
    st.subheader("Seller Verification Status")
    st.caption("Understand the current verification workload.")
    status_chart = verification_df.set_index("verification_status")[
        ["seller_count"]
    ]
    st.bar_chart(status_chart, color=TAUPE)
    st.dataframe(
        verification_df,
        width="stretch",
        hide_index=True,
    )

st.subheader("Seller Registration Trend")
st.caption("Monthly registrations from the generated dataset.")

monthly_df["registration_date"] = pd.to_datetime(
    monthly_df[["year", "month"]].assign(day=1)
)
monthly_chart = monthly_df.set_index("registration_date")[["sellers"]]
st.line_chart(monthly_chart, color=WALNUT)

status_columns = st.columns(3)
show_kpi(status_columns[0], "Approved", f"{approved:,}", AMBER)
show_kpi(status_columns[1], "Pending", f"{pending:,}", TAUPE)
show_kpi(status_columns[2], "Rejected", f"{rejected:,}", CORAL)

st.divider()
st.markdown("### Explore the dashboard")
st.write(
    "Use the sidebar to open **Revenue & Markets**, **Seller Verification**, "
    "**Risk & Refunds**, **Registration Trends**, **Data Quality**, "
    "and **Reports & Exports**."
)
st.caption(
    "Seller Verification Data Engineering Platform | "
    "Python Â· Pandas Â· DuckDB Â· Streamlit"
)
