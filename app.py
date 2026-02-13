import streamlit as st
import io

from backend.metadata_extractor import extract_global_metadata, extract_page_metadata
from backend.piping_extractor import extract_pipes_from_page
from backend.sheetmetal_extractor import extract_ducts_from_page

st.set_page_config(page_title="HVAC AI", layout="wide")
st.title("HVAC Drawing Extraction System")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file is None:
    st.warning("Please upload a PDF file to continue.")
    st.stop()

st.success("PDF uploaded successfully")
pdf_bytes = io.BytesIO(uploaded_file.read())
pdf_bytes.seek(0)
st.sidebar.header("Controls")
option = st.sidebar.selectbox(
    "Select Extraction Type",
    ["Metadata", "Piping", "Sheet Metal"]
)

page_number = st.sidebar.number_input(
    "Enter Page Number",
    min_value=1,
    max_value=200,
    value=1,
    step=1
)

if option == "Metadata":
    st.subheader("Metadata Extraction")
    pdf_bytes.seek(0)
    global_data = extract_global_metadata(pdf_bytes)
    pdf_bytes.seek(0)
    page_data = extract_page_metadata(pdf_bytes, page_number)
    final_output = {**global_data, **page_data}
    st.json(final_output)

elif option == "Piping":
    st.subheader("Piping Extraction")
    pdf_bytes.seek(0)
    pipes = extract_pipes_from_page(pdf_bytes, page_number)
    st.write(f"Pipes Found: {len(pipes)}")
    if pipes:
        st.json(pipes[:50])

elif option == "Sheet Metal":
    st.subheader("Sheet Metal Extraction")
    pdf_bytes.seek(0)
    ducts = extract_ducts_from_page(pdf_bytes, page_number)
    st.write(f"Ducts Found: {len(ducts)}")
    if ducts:
        st.json(ducts[:50])
