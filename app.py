import streamlit as st
import pandas as pd
from forex_python.converter import CurrencyRates

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SAC Style Currency Conversion",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* App */
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

# ---------------- MAIN ----------------
if uploaded_file is not None:

    # Read file
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

        # First Row
        html += "<tr>"

        for d in dimensions:
            html += '<th class="blank-head"></th>'

        html += f'''
        <th class="measure-group" colspan="{len(measures)}">
            Measures
        </th>
        '''

        html += "</tr>"

        # Second Row
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
    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True
    )

    st.subheader("Currency Conversion")

    # Check Currency Column
    if "Currency" not in df.columns:

        st.warning(
            "Currency column not found in uploaded file."
        )

    else:

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

        # Amount Column
        amount_col = st.selectbox(
            "Select Amount Column",
            numeric_cols
        )

        # ---------------- CONVERT BUTTON ----------------
        if st.button("Convert Currency"):

            try:

                converted_df = df.copy()

                # IMPORTANT FIX
                converted_df[amount_col] = pd.to_numeric(
                    converted_df[amount_col],
                    errors="coerce"
                ).astype(float)

                # Currency API
                c = CurrencyRates()

                # Get Exchange Rate
                rate = c.get_rate(
                    from_currency,
                    to_currency
                )

                # Convert ONLY selected currency rows
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

                # Update currency
                converted_df.loc[
                    mask,
                    "Currency"
                ] = to_currency

                # Success Message
                st.success(
                    f"1 {from_currency} = "
                    f"{rate:.2f} {to_currency}"
                )

                # Converted Table
                st.subheader("Converted Table")

                st.markdown(
                    build_table(converted_df),
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"Conversion Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Upload CSV or Excel File")
