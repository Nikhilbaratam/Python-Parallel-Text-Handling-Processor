import streamlit as st
import pandas as pd

# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="Parallel Text Handling Processor",
    page_icon="⚡",
    layout="wide"
)

# -------------------------
# Centered Project Title
# -------------------------
st.markdown(
    "<h1 style='text-align: center;'>⚡ Parallel Text Handling Processor</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Upload a CSV file containing ONLY text data.</p>",
    unsafe_allow_html=True
)

st.divider()

# -------------------------
# File Upload
# -------------------------
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file, encoding="latin1", engine="python")

        # Detect numeric columns
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

        if len(numeric_columns) > 0:
            st.error("❌ Invalid File: CSV contains numerical columns.")
            st.write("Numeric Columns Detected:", numeric_columns)
            st.stop()

        # If no numeric columns → Accept file
        st.success("✅ Valid File: Only text data detected.")

        st.subheader("📊 Dataset Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.write("Columns:", list(df.columns))

    except Exception as e:
        st.error(f"⚠ Error reading file: {e}")