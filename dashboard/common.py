
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = PROJECT_ROOT / "dashboard" / "exports"

WALNUT = "#674D3C"
AMBER = "#D9AD7C"
TAUPE = "#A2836E"
PEACH = "#F9CCAC"
CORAL = "#F4A688"
INK = "#3F3028"
MUTED = "#76665A"
BORDER = "#E5D9CD"


@st.cache_data
def load_csv(filename):
    path = EXPORT_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path)


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
        .page-header {{
            background: #FFFFFF;
            border: 1px solid {BORDER};
            border-left: 6px solid {WALNUT};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.2rem;
        }}
        .page-header h1 {{
            color: {WALNUT};
            margin: 0;
            font-size: 1.9rem;
        }}
        .page-header p {{
            color: {MUTED};
            margin: .4rem 0 0 0;
        }}
        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid {BORDER};
            border-top: 4px solid {AMBER};
            border-radius: 10px;
            padding: 1rem;
            min-height: 105px;
        }}
        .kpi-label {{
            color: {MUTED};
            font-size: .85rem;
        }}
        .kpi-value {{
            color: {WALNUT};
            font-size: 1.7rem;
            font-weight: 700;
            margin-top: .25rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="page-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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


def require_data(*datasets):
    """Stop a page gracefully when one or more exports are missing."""
    missing = [
        name for name, dataframe in datasets
        if dataframe is None
    ]

    if missing:
        st.error(
            "Required exports are missing. Run the pipeline first."
        )
        st.write("Missing exports:", missing)
        st.stop()


def format_inr(value, decimals=0):
    """Format a numeric value as Indian Rupees with Indian digit grouping."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "₹0"

    if not pd.notna(amount):
        return "₹0"

    sign = "-" if amount < 0 else ""
    amount = abs(amount)

    formatted = f"{amount:.{decimals}f}"
    integer_part, _, decimal_part = formatted.partition(".")

    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []

        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            groups.insert(0, remaining)

        integer_part = ",".join(groups) + "," + last_three

    result = f"{sign}₹{integer_part}"
    if decimals:
        result += f".{decimal_part}"

    return result


def format_inr(value, decimals=0):
    """Format a value as Indian Rupees using Indian digit grouping."""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "₹0"

    if not pd.notna(amount):
        return "₹0"

    sign = "-" if amount < 0 else ""
    formatted = f"{abs(amount):.{decimals}f}"
    integer_part, _, decimal_part = formatted.partition(".")

    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []

        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            groups.insert(0, remaining)

        integer_part = ",".join(groups) + "," + last_three

    result = f"{sign}₹{integer_part}"

    if decimals:
        result += f".{decimal_part}"

    return result
