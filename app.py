import streamlit as st
import pandas as pd
from forex_python.converter import CurrencyRates

# Page Config
st.set_page_config(
    page_title="SAC Style Currency Conversion",
    layout="wide"
)

# Load CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="top-header">
        New_Analytic_Model
    </div>
    """,
    unsafe_allow_html=True
)

# Upload File
uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

    # Detect Dimensions & Measures
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

    # Arrange columns
    ordered_cols = dimensions + measures

    # SAC Style Table
    html = """
    <div class="table-wrapper">
    <table>
    <thead>
    """

    # First Header Row
    html += "<tr>"

    for d in dimensions:
        html += '<th class="blank-head"></th>'

    html += f'''
    <th class="measure-group" colspan="{len(measures)}">
        Measures
    </th>
    '''

    html += "</tr>"

    # Second Header Row
    html += "<tr>"

    for col in ordered_cols:

        if col in measures:
            html += f'<th class="measure-col">{col}</th>'

        else:
            html += f'<th class="dimension-col">{col}</th>'

    html += "</tr></thead>"

    # Body
    html += "<tbody>"

    for _, row in df.iterrows():

        html += "<tr>"

        for col in ordered_cols:
            html += f"<td>{row[col]}</td>"

        html += "</tr>"

    html += "</tbody></table></div>"

    # Display table
    st.markdown(html, unsafe_allow_html=True)

    # Currency Conversion Section
    st.markdown(
        """
        <div class="currency-box">
        """,
        unsafe_allow_html=True
    )

    st.subheader("Currency Conversion")

    # Currency List
    currencies = sorted(df["Currency"].dropna().unique())

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

    # Numeric columns
    numeric_cols = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    # Amount column
    amount_col = st.selectbox(
        "Select Amount Column",
        numeric_cols
    )

    # Convert Button
    if st.button("Convert Currency"):

        try:

            # Currency API
            c = CurrencyRates()

            # Copy dataframe
            converted_df = df.copy()

            # Exchange Rate
            rate = c.get_rate(
                from_currency,
                to_currency
            )

            # ONLY selected currency rows convert
            mask = converted_df["Currency"] == from_currency

            converted_df.loc[mask, amount_col] = (
                converted_df.loc[mask, amount_col] * rate
            ).round(2)

            # Update currency column
            converted_df.loc[mask, "Currency"] = to_currency

            # Success message
            st.success(
                f"1 {from_currency} = {rate:.2f} {to_currency}"
            )

            # Rebuild SAC Table
            html2 = """
            <div class="table-wrapper">
            <table>
            <thead>
            """

            html2 += "<tr>"

            for d in dimensions:
                html2 += '<th class="blank-head"></th>'

            html2 += f'''
            <th class="measure-group" colspan="{len(measures)}">
                Measures
            </th>
            '''

            html2 += "</tr>"

            html2 += "<tr>"

            for col in ordered_cols:

                if col in measures:
                    html2 += f'<th class="measure-col">{col}</th>'

                else:
                    html2 += f'<th class="dimension-col">{col}</th>'

            html2 += "</tr></thead>"

            html2 += "<tbody>"

            for _, row in converted_df.iterrows():

                html2 += "<tr>"

                for col in ordered_cols:
                    html2 += f"<td>{row[col]}</td>"

                html2 += "</tr>"

            html2 += "</tbody></table></div>"

            st.subheader("Converted Table")

            st.markdown(html2, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Upload CSV or Excel File")
