import streamlit as st
import pandas as pd
from forex_python.converter import CurrencyRates

# Page Config
st.set_page_config(
    page_title="Simple Currency Converter Table",
    layout="wide"
)

# Load CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown(
    '<div class="top-header">Currency Conversion Table</div>',
    unsafe_allow_html=True
)

# Upload
uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Original Table")

    st.dataframe(df, use_container_width=True)

    # Currency Conversion Box
    st.markdown(
        '<div class="currency-box">',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    # Currency Options
    currencies = [
        "USD",
        "EUR",
        "INR",
        "GBP",
        "JPY",
        "AED",
        "SGD"
    ]

    with col1:
        from_currency = st.selectbox(
            "From Currency",
            currencies
        )

    with col2:
        to_currency = st.selectbox(
            "To Currency",
            currencies,
            index=2
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Detect numeric columns
    numeric_cols = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    # Select amount column
    amount_col = st.selectbox(
        "Select Amount Column",
        numeric_cols
    )

    # Convert Button
    if st.button("Convert Currency"):

        c = CurrencyRates()

        try:

            # Get Rate
            rate = c.get_rate(
                from_currency,
                to_currency
            )

            # Convert
            df["Converted Amount"] = (
                df[amount_col] * rate
            ).round(2)

            st.success(
                f"Conversion Rate: 1 {from_currency} = {rate:.2f} {to_currency}"
            )

            st.subheader("Converted Table")

            st.dataframe(
                df,
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error: {e}")
