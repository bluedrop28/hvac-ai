import streamlit as st
import os

from backend.metadata_extractor import extract_global_metadata, extract_page_metadata
from backend.piping_extractor import extract_pipes_from_page
from backend.sheetmetal_extractor import extract_ducts_from_page

st.set_page_config(page_title="HVAC AI", layout="wide")
st.title("HVAC Drawing Extraction System")

# PDF Path

pdf_path = "Vital A1-A2 HVAC Drawings.pdf"
if not os.path.exists(pdf_path):
    st.error("PDF file not found in project folder.")
    st.stop()

# Sidebar Controls
 
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

# METADATA

if option == "Metadata":
    st.subheader("Metadata Extraction")
    global_data = extract_global_metadata(pdf_path)
    page_data = extract_page_metadata(pdf_path, page_number)
    final_output = {**global_data, **page_data}
    st.json(final_output)

# PIPING

elif option == "Piping":
    st.subheader("Piping Extraction")
    pipes = extract_pipes_from_page(pdf_path, page_number)
    st.write(f"Pipes Found: {len(pipes)}")
    if pipes:
        st.json(pipes[:50])  # show first 50 only

# SHEET METAL

elif option == "Sheet Metal":
    st.subheader("Sheet Metal Extraction")
    ducts = extract_ducts_from_page(pdf_path, page_number)
    st.write(f"Ducts Found: {len(ducts)}")
    if ducts:
        st.json(ducts[:50])  # show first 50 only
