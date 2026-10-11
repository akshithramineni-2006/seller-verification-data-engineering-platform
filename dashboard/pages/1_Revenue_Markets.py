
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
    page_title="Revenue & Markets",
    page_icon="💰",
    layout="wide",
)

inject_styles()

page_header(
    "Revenue & Markets",
    "Explore sales performance across countries, business types, and industries.",
)

# Load analytics exports
country_df = load_csv("revenue_by_country.csv")
business_df = load_csv("revenue_by_business.csv")
industry_df = load_csv("industry_revenue.csv")
refund_df = load_csv("refund_rate.csv")

require_data(
    ("Revenue by country", country_df),
    ("Revenue by business type", business_df),
    ("Industry revenue", industry_df),
    ("Refund rates", refund_df),
)

# Validate expected columns
required_columns = [
    (country_df, {"country_name", "total_sales"}, "Country revenue"),
    (business_df, {"business_type", "total_sales"}, "Business revenue"),
    (industry_df, {"industry", "avg_revenue"}, "Industry revenue"),
    (
        refund_df,
        {"business_type", "refund_percentage"},
        "Refund rates",
    ),
]

for dataframe, expected, label in required_columns:
    if not expected.issubset(dataframe.columns):
        st.error(
            f"{label} export is missing columns: "
            f"{', '.join(sorted(expected - set(dataframe.columns)))}"
        )
        st.stop()

# Sidebar filters
st.sidebar.subheader("Market Filters")

countries = sorted(
    country_df["country_name"].dropna().astype(str).unique().tolist()
)
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=countries,
    default=countries,
)

business_types = sorted(
    business_df["business_type"].dropna().astype(str).unique().tolist()
)
selected_business_types = st.sidebar.multiselect(
    "Business types",
    options=business_types,
    default=business_types,
)

filtered_country = country_df[
    country_df["country_name"].astype(str).isin(selected_countries)
].copy()

filtered_business = business_df[
    business_df["business_type"].astype(str).isin(selected_business_types)
].copy()

# Prepare numeric values
filtered_country["total_sales"] = __import__("pandas").to_numeric(
    filtered_country["total_sales"], errors="coerce"
).fillna(0)

filtered_business["total_sales"] = __import__("pandas").to_numeric(
    filtered_business["total_sales"], errors="coerce"
).fillna(0)

industry_chart = industry_df.copy()
industry_chart["avg_revenue"] = __import__("pandas").to_numeric(
    industry_chart["avg_revenue"], errors="coerce"
)

refund_chart = refund_df.copy()
refund_chart["refund_percentage"] = __import__("pandas").to_numeric(
    refund_chart["refund_percentage"], errors="coerce"
).fillna(0)

total_revenue = float(filtered_country["total_sales"].sum())
country_count = len(filtered_country)

if not filtered_country.empty:
    leading_country = filtered_country.loc[
        filtered_country["total_sales"].idxmax(), "country_name"
    ]
else:
    leading_country = "—"

if not filtered_business.empty:
    leading_business = filtered_business.loc[
        filtered_business["total_sales"].idxmax(), "business_type"
    ]
else:
    leading_business = "—"

average_refund = (
    float(refund_chart["refund_percentage"].mean())
    if not refund_chart.empty
    else 0
)

# KPI cards
st.subheader("Market Performance")

kpis = st.columns(4)

show_kpi(
    kpis[0],
    "Revenue in Selected Countries",
    format_inr(total_revenue),
    AMBER,
)

show_kpi(
    kpis[1],
    "Countries Selected",
    f"{country_count:,}",
    WALNUT,
)

show_kpi(
    kpis[2],
    "Leading Country",
    str(leading_country),
    TAUPE,
)

show_kpi(
    kpis[3],
    "Average Refund Rate",
    f"{average_refund:.2f}%",
    CORAL,
)

st.divider()

# Revenue by country
st.subheader("Revenue by Country")
st.caption("Compare total sales across seller markets. Currency: Indian Rupees (₹ INR).")

if filtered_country.empty:
    st.info("Select at least one country in the sidebar.")
else:
    country_chart = filtered_country.sort_values(
        "total_sales", ascending=True
    )

    st.bar_chart(
        country_chart,
        x="country_name",
        y="total_sales",
        color=AMBER,
        horizontal=True,
    )

    country_details = country_chart.copy()
    country_details["Revenue (₹ INR)"] = country_details["total_sales"].map(
        format_inr
    )

    st.dataframe(
        country_details.drop(columns=["total_sales"]),
        width="stretch",
        hide_index=True,
    )

st.divider()

# Revenue by business type
st.subheader("Revenue by Business Type")
st.caption("Compare sales across business structures. Currency: ₹ INR.")

if filtered_business.empty:
    st.info("Select at least one business type in the sidebar.")
else:
    business_chart = filtered_business.sort_values(
        "total_sales", ascending=True
    )

    st.bar_chart(
        business_chart,
        x="business_type",
        y="total_sales",
        color=WALNUT,
        horizontal=True,
    )

    business_details = business_chart.copy()
    business_details["Revenue (₹ INR)"] = business_details[
        "total_sales"
    ].map(format_inr)

    st.dataframe(
        business_details.drop(columns=["total_sales"]),
        width="stretch",
        hide_index=True,
    )

st.divider()

# Average revenue by industry
st.subheader("Average Revenue by Industry")
st.caption("Compare average revenue across industries. Currency: ₹ INR.")

industry_sorted = industry_chart.dropna(
    subset=["avg_revenue"]
).sort_values("avg_revenue", ascending=True)

if industry_sorted.empty:
    st.info("No industry revenue records are available.")
else:
    st.bar_chart(
        industry_sorted,
        x="industry",
        y="avg_revenue",
        color=TAUPE,
        horizontal=True,
    )

    industry_details = industry_sorted.copy()
    industry_details["Average Revenue (₹ INR)"] = industry_details[
        "avg_revenue"
    ].map(format_inr)

    st.dataframe(
        industry_details.drop(columns=["avg_revenue"]),
        width="stretch",
        hide_index=True,
    )

st.divider()

# Refund rates
st.subheader("Refund Rate by Business Type")
st.caption("Refund percentages are rates, not currency amounts.")

refund_sorted = refund_chart.sort_values(
    "refund_percentage", ascending=True
)

st.bar_chart(
    refund_sorted,
    x="business_type",
    y="refund_percentage",
    color=CORAL,
    horizontal=True,
)

st.dataframe(
    refund_sorted,
    width="stretch",
    hide_index=True,
)

st.caption(
    "Revenue values are displayed in Indian Rupees. The source CSV exports "
    "and underlying numeric values remain unchanged."
)
