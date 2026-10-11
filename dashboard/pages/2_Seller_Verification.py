
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
    page_title="Seller Verification",
    page_icon="âœ…",
    layout="wide",
)

inject_styles()
page_header(
    "Seller Verification",
    "Monitor approval outcomes, pending verification, and country-level performance.",
)

status_df = load_csv("verification_status.csv")
country_status_df = load_csv("country_verification.csv")

require_data(
    ("Verification status", status_df),
    ("Country verification", country_status_df),
)

# Calculate the headline metrics
total_sellers = int(status_df["seller_count"].sum())


def count_status(status):
    return int(
        status_df.loc[
            status_df["verification_status"].str.casefold(
            ) == status.casefold(),
            "seller_count",
        ].sum()
    )


approved = count_status("Approved")
pending = count_status("Pending")
rejected = count_status("Rejected")

approval_rate = approved / total_sellers * 100 if total_sellers else 0
rejection_rate = rejected / total_sellers * 100 if total_sellers else 0

kpis = st.columns(4)
show_kpi(kpis[0], "Total Sellers", f"{total_sellers:,}", WALNUT)
show_kpi(kpis[1], "Approved", f"{approved:,}", AMBER)
show_kpi(kpis[2], "Approval Rate", f"{approval_rate:.1f}%", TAUPE)
show_kpi(kpis[3], "Rejection Rate", f"{rejection_rate:.1f}%", CORAL)

st.write("")

left, right = st.columns(2)

with left:
    st.subheader("Verification Outcomes")
    st.caption("Compare the number of sellers in each verification state.")
    st.bar_chart(
        status_df,
        x="verification_status",
        y="seller_count",
        color=AMBER,
    )

with right:
    st.subheader("Verification Share")
    st.caption("Share of sellers by verification status.")
    share_df = status_df.set_index("verification_status")[["seller_count"]]
    st.bar_chart(share_df, color=TAUPE)

st.divider()
st.subheader("Verification by Country")
st.caption("Use the filters to compare country-level outcomes.")

countries = sorted(
    country_status_df["country_name"].dropna().unique()
)
selected_countries = st.multiselect(
    "Countries",
    options=countries,
    default=countries,
    key="verification_countries",
)

filtered = country_status_df[
    country_status_df["country_name"].isin(selected_countries)
]

if filtered.empty:
    st.info("Select at least one country to display verification results.")
else:
    pivot = filtered.pivot_table(
        index="country_name",
        columns="verification_status",
        values="seller_count",
        aggfunc="sum",
        fill_value=0,
    )
    st.bar_chart(pivot)

    st.dataframe(
        filtered.sort_values(
            ["country_name", "verification_status"]
        ),
        width="stretch",
        hide_index=True,
    )

st.subheader("Verification Rate by Country")

if not filtered.empty:
    country_totals = (
        filtered.groupby("country_name", as_index=False)["seller_count"]
        .sum()
        .rename(columns={"seller_count": "total_sellers"})
    )

    approved_by_country = (
        filtered.loc[
            filtered["verification_status"].eq("Approved")
        ]
        .groupby("country_name", as_index=False)["seller_count"]
        .sum()
        .rename(columns={"seller_count": "approved_sellers"})
    )

    rates = country_totals.merge(
        approved_by_country,
        on="country_name",
        how="left",
    )
    rates["approved_sellers"] = rates["approved_sellers"].fillna(0)
    rates["approval_rate"] = (
        rates["approved_sellers"] / rates["total_sellers"] * 100
    )

    st.bar_chart(
        rates.sort_values("approval_rate"),
        x="country_name",
        y="approval_rate",
        horizontal=True,
        color=WALNUT,
    )
    st.dataframe(rates, width="stretch", hide_index=True)

st.caption(
    "Verification figures are based on the current analytics exports."
)

