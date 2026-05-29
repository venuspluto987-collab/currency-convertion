import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SAC Style Currency Conversion",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: #f4f5f7;
    font-family: Arial, sans-serif;
}

/* Header */
.main-title {
    font-size: 38px;
    color: #555;
    margin-bottom: 20px;
    font-weight: 500;
}

/* Upload Box */
[data-testid="stFileUploader"] {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
}

/* Section Box */
.section-box {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-top: 20px;
}

/* Table */
table {
    border-collapse: collapse;
    width: 100%;
}

/* Measure Group */
.measure-group {
    background-color: #f3f3f3;
    text-align: center;
    font-size: 24px;
    color: #444;
    height: 50px;
    border-bottom: 2px solid #ddd;
}

/* Blank Header */
.blank-head {
    background-color: #f3f3f3;
    border-bottom: 2px solid #ddd;
}

/* Dimension Header */
.dimension-col {
    background-color: #fafafa;
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #ddd;
    font-size: 18px;
}

/* Measure Header */
.measure-col {
    background-color: #fafafa;
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #ddd;
    font-size: 18px;
}

/* Table Cell */
td {
    padding: 12px;
    border-bottom: 1px solid #eee;
    font-size: 16px;
}

/* Hover */
tr:hover {
    background-color: #f9fbfd;
}

/* Success */
.success-box {
    background-color: #e8f5e9;
    color: #2e7d32;
    padding: 12px;
    border-radius: 10px;
    margin-top: 15px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">New_Analytic_Model</div>',
    unsafe_allow_html=True
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

# ---------------- EXCHANGE RATES ----------------
exchange_rates = {

    "USD": {
        "INR": 83.0,
        "EUR": 0.92,
        "AED": 3.67,
        "GBP": 0.79,
        "SGD": 1.35,
        "JPY": 156.0
    },

    "INR": {
        "USD": 0.012,
        "EUR": 0.011,
        "AED": 0.044,
        "GBP": 0.0095,
        "SGD": 0.016,
        "JPY": 1.88
    },

    "EUR": {
        "USD": 1.09,
        "INR": 90.0,
        "AED": 4.0,
        "GBP": 0.86,
        "SGD": 1.47,
        "JPY": 170.0
    },

    "AED": {
        "USD": 0.27,
        "INR": 22.6,
        "EUR": 0.25,
        "GBP": 0.21,
        "SGD": 0.37,
        "JPY": 42.5
    },

    "GBP": {
        "USD": 1.27,
        "INR": 105.0,
        "EUR": 1.16,
        "AED": 4.67,
        "SGD": 1.71,
        "JPY": 198.0
    },

    "SGD": {
        "USD": 0.74,
        "INR": 61.0,
        "EUR": 0.68,
        "AED": 2.72,
        "GBP": 0.58,
        "JPY": 116.0
    },

    "JPY": {
        "USD": 0.0064,
        "INR": 0.53,
        "EUR": 0.0059,
        "AED": 0.024,
        "GBP": 0.005,
        "SGD": 0.0086
    }
}

# ---------------- MAIN ----------------
if uploaded_file is not None:

    # Read File
    try:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        else:
            df = pd.read_excel(uploaded_file)

    except Exception as e:
        st.error(f"File Read Error: {e}")
        st.stop()

    # ---------------- DETECT DIMENSIONS & MEASURES ----------------
    dimensions = []
    measures = []

    for col in df.columns:

        if (
            pd.api.types.is_numeric_dtype(df[col])
            and "id" not in col.lower()
        ):
            measures.append(col)

        else:
            dimensions.append(col)

    ordered_cols = dimensions + measures

    # ---------------- TABLE FUNCTION ----------------
    def build_table(dataframe):

        html = """
        <div class="section-box">
        <table>
        <thead>
        """

        # Header Row 1
        html += "<tr>"

        for d in dimensions:
            html += '<th class="blank-head"></th>'

        html += f'''
        <th class="measure-group" colspan="{len(measures)}">
            Measures
        </th>
        '''

        html += "</tr>"

        # Header Row 2
        html += "<tr>"

        for col in ordered_cols:

            if col in measures:
                html += f'<th class="measure-col">{col}</th>'

            else:
                html += f'<th class="dimension-col">{col}</th>'

        html += "</tr>"

        html += "</thead><tbody>"

        # Data Rows
        for _, row in dataframe.iterrows():

            html += "<tr>"

            for col in ordered_cols:
                html += f"<td>{row[col]}</td>"

            html += "</tr>"

        html += "</tbody></table></div>"

        return html

    # ---------------- ORIGINAL TABLE ----------------
    st.subheader("Original Table")

    st.markdown(
        build_table(df),
        unsafe_allow_html=True
    )

    # ---------------- CURRENCY SECTION ----------------
    if "Currency" in df.columns:

        st.subheader("Currency Conversion")

        currencies = sorted(
            df["Currency"].dropna().unique().tolist()
        )

        col1, col2 = st.columns(2)

        with col1:
            from_currency = st.selectbox(
                "From Currency",
                currencies
            )

        with col2:
            to_currency = st.selectbox(
                "To Currency",
                currencies
            )

        # Numeric Columns
        numeric_cols = df.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()

        amount_col = st.selectbox(
            "Select Amount Column",
            numeric_cols
        )

        # ---------------- CONVERT BUTTON ----------------
        if st.button("Convert Currency"):

            try:

                converted_df = df.copy()

                # Convert amount column to float
                converted_df[amount_col] = pd.to_numeric(
                    converted_df[amount_col],
                    errors="coerce"
                ).astype(float)

                # Same Currency
                if from_currency == to_currency:
                    rate = 1

                else:
                    rate = exchange_rates[
                        from_currency
                    ][to_currency]

                # Convert ONLY selected rows
                mask = (
                    converted_df["Currency"]
                    == from_currency
                )

                converted_df.loc[
                    mask,
                    amount_col
                ] = (
                    converted_df.loc[
                        mask,
                        amount_col
                    ] * rate
                ).round(2)

                # Update Currency Column
                converted_df.loc[
                    mask,
                    "Currency"
                ] = to_currency

                # Success Message
                st.markdown(
                    f"""
                    <div class="success-box">
                        1 {from_currency} =
                        {rate:.2f} {to_currency}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Converted Table
                st.subheader("Converted Table")

                st.markdown(
                    build_table(converted_df),
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"Conversion Error: {e}")

    else:
        st.warning(
            "Currency column not found in uploaded file."
        )

else:
    st.info("Upload CSV or Excel File")
