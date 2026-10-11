
import pandas as pd
import streamlit as st

from dashboard.common import (
    AMBER,
    CORAL,
    TAUPE,
    WALNUT,
    inject_styles,
    load_csv,
    page_header,
    require_data,
    show_kpi,
)

st.set_page_config(
    page_title="Registration Trends",
    page_icon="ðŸ“ˆ",
    layout="wide",
)

inject_styles()
page_header(
    "Registration Trends",
    "Explore seller onboarding patterns over time and identify registration peaks.",
)

monthly_df = load_csv("monthly_registrations.csv")

require_data(("Monthly registrations", monthly_df))

required_columns = {"year", "month", "seller_count"}
if not required_columns.issubset(monthly_df.columns):
    st.error(
        "The monthly registrations export must contain "
        "year, month, and seller_count columns."
    )
    st.stop()

df = monthly_df.copy()
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["month"] = pd.to_numeric(df["month"], errors="coerce")
df["seller_count"] = pd.to_numeric(df["seller_count"], errors="coerce")
df = df.dropna(subset=["year", "month", "seller_count"])

df["year"] = df["year"].astype(int)
df["month"] = df["month"].astype(int)
df = df[df["month"].between(1, 12)]

month_names = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

df["month_name"] = df["month"].map(month_names)
df["period"] = pd.to_datetime(
    dict(year=df["year"], month=df["month"], day=1)
)
df = df.sort_values("period")

if df.empty:
    st.warning("No valid monthly registration records were found.")
    st.stop()

year_options = sorted(df["year"].unique(), reverse=True)
selected_years = st.multiselect(
    "Filter by year",
    options=sorted(year_options),
    default=sorted(year_options),
)

filtered = df[df["year"].isin(selected_years)].copy()

if filtered.empty:
    st.info("Select at least one year to view registration trends.")
    st.stop()

total_registrations = int(filtered["seller_count"].sum())
average_monthly = float(filtered["seller_count"].mean())
peak_row = filtered.loc[filtered["seller_count"].idxmax()]
years_in_view = filtered["year"].nunique()

kpis = st.columns(4)
show_kpi(
    kpis[0], "Total Registrations", f"{total_registrations:,}", WALNUT
)
show_kpi(
    kpis[1], "Average per Month", f"{average_monthly:,.0f}", AMBER
)
show_kpi(
    kpis[2],
    "Peak Month",
    f"{peak_row['month_name']} {int(peak_row['year'])}",
    CORAL,
)
show_kpi(
    kpis[3], "Years Selected", f"{years_in_view}", TAUPE
)

st.write("")

st.subheader("Monthly Registration Trend")
st.caption(
    "Track changes in registrations across the selected years."
)

trend = filtered.set_index("period")[["seller_count"]]
st.line_chart(trend, color=AMBER)

left, right = st.columns(2)

with left:
    st.subheader("Registrations by Year")
    yearly = (
        filtered.groupby("year", as_index=False)["seller_count"]
        .sum()
        .sort_values("year")
    )
    st.bar_chart(
        yearly,
        x="year",
        y="seller_count",
        color=WALNUT,
    )

with right:
    st.subheader("Registrations by Calendar Month")
    monthly = (
        filtered.groupby("month", as_index=False)["seller_count"]
        .sum()
        .sort_values("month")
    )
    monthly["month_name"] = monthly["month"].map(month_names)
    monthly = monthly.sort_values("month")
    st.bar_chart(
        monthly,
        x="month_name",
        y="seller_count",
        color=TAUPE,
    )

st.divider()
st.subheader("Monthly Registration Details")

details = filtered[
    ["year", "month_name", "seller_count"]
].rename(
    columns={
        "year": "Year",
        "month_name": "Month",
        "seller_count": "Registrations",
    }
)

st.dataframe(
    details.sort_values(["Year", "Month"]),
    width="stretch",
    hide_index=True,
)

st.caption(
    "Interpret the latest year carefully if it contains only partial-year data."
)

