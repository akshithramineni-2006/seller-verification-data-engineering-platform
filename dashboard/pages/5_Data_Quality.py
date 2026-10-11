
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
    page_title="Data Quality",
    page_icon="✅",
    layout="wide",
)

inject_styles()
page_header(
    "Data Quality",
    "Review pipeline validation checks and identify records requiring attention.",
)

quality_df = load_csv("quality_report.csv")
require_data(("Data quality report", quality_df))

if not {"Check", "Count"}.issubset(quality_df.columns):
    st.error(
        "The quality report must contain 'Check' and 'Count' columns."
    )
    st.stop()

df = quality_df.copy()
df["Count"] = pd.to_numeric(df["Count"], errors="coerce").fillna(0)
df["Check"] = df["Check"].astype(str)

if df.empty:
    st.info("The quality report contains no checks.")
    st.stop()

total_checks = len(df)
passed_checks = int((df["Count"] == 0).sum())
failed_checks = total_checks - passed_checks
total_issues = int(df["Count"].clip(lower=0).sum())

kpis = st.columns(4)
show_kpi(kpis[0], "Total Checks", f"{total_checks}", WALNUT)
show_kpi(kpis[1], "Checks Passed", f"{passed_checks}", AMBER)
show_kpi(kpis[2], "Checks With Issues", f"{failed_checks}", CORAL)
show_kpi(kpis[3], "Reported Issues", f"{total_issues:,}", TAUPE)

st.divider()

if failed_checks == 0:
    st.success("All reported checks have zero issues.")
else:
    st.warning(
        f"{failed_checks} check(s) reported non-zero issue counts."
    )

left, right = st.columns(2)

with left:
    st.subheader("Issues by Validation Check")
    st.caption("Zero means that the check found no problematic records.")

    chart_df = df.sort_values("Count", ascending=True)
    st.bar_chart(
        chart_df,
        x="Check",
        y="Count",
        color=CORAL,
        horizontal=True,
    )

with right:
    st.subheader("Validation Results")
    results = df.copy()
    results["Status"] = results["Count"].apply(
        lambda count: "PASS" if count == 0 else "REVIEW"
    )
    results = results.rename(
        columns={"Check": "Validation Check", "Count": "Issue Count"}
    )
    st.dataframe(
        results[["Validation Check", "Issue Count", "Status"]],
        width="stretch",
        hide_index=True,
    )

st.divider()
st.subheader("How to Interpret This Report")

st.markdown(
    """
    - **PASS:** The check reported zero issues.
    - **REVIEW:** The check reported one or more issues.
    - **Reported Issues:** The sum of the non-negative counts in the report.

    These results describe the checks recorded in the latest quality report.
    They do not independently prove that every possible data-quality problem
    has been detected.
    """
)

st.download_button(
    "Download Quality Report",
    data=quality_df.to_csv(index=False).encode("utf-8"),
    file_name="quality_report.csv",
    mime="text/csv",
)
