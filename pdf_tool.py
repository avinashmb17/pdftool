import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import os

st.set_page_config(page_title="PDF Merge & Split Tool", layout="wide")

st.title("📄 PDF Merge & Split Tool")

# ---------------- SESSION STATE ----------------
if "mode" not in st.session_state:
    st.session_state.mode = "merge"

if "pages" not in st.session_state:
    st.session_state.pages = []

# ---------------- MODE ----------------
st.radio(
    "Select Mode",
    ["merge", "split"],
    key="mode"
)

# =========================================================
# MERGE MODE
# =========================================================
if st.session_state.mode == "merge":

   # st.subheader("🔀 Merge PDFs (Page-wise control)")
    st.subheader(" Merge PDFs (Page-wise control)")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    # LOAD PAGES
    if uploaded_files:
        if st.button("Load Pages"):
            st.session_state.pages = []

            for file in uploaded_files:
                file_bytes = file.getvalue()
                reader = PdfReader(io.BytesIO(file_bytes))

                for i in range(len(reader.pages)):
                    st.session_state.pages.append(
                        (file.name, file_bytes, i)
                    )

            st.success("Pages loaded successfully!")

    # SHOW PAGES
    st.write("### Pages Order")

    for idx, (fname, _, page_num) in enumerate(st.session_state.pages):
        st.write(f"{idx+1}. {fname} - Page {page_num+1}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Move Last Up"):
            if len(st.session_state.pages) > 1:
                i = len(st.session_state.pages) - 1
                st.session_state.pages[i-1], st.session_state.pages[i] = (
                    st.session_state.pages[i],
                    st.session_state.pages[i-1]
                )

    with col2:
        if st.button("Move First Down"):
            if len(st.session_state.pages) > 1:
                i = 0
                st.session_state.pages[i], st.session_state.pages[i+1] = (
                    st.session_state.pages[i+1],
                    st.session_state.pages[i]
                )

    # MERGE PDF
    if st.button("Merge PDFs"):
        if not st.session_state.pages:
            st.warning("No pages selected.")
        else:
            writer = PdfWriter()

            for fname, file_bytes, page_num in st.session_state.pages:
                reader = PdfReader(io.BytesIO(file_bytes))

                if page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])

            output = io.BytesIO()
            writer.write(output)
            output.seek(0)

            st.success("PDF merged successfully!")

            st.download_button(
                "Download Merged PDF",
                data=output,
                file_name="merged.pdf",
                mime="application/pdf"
            )

# =========================================================
# SPLIT MODE (FIXED + STABLE)
# =========================================================
else:

    #st.subheader("✂️ Split PDF (Upload + Save to Folder)")
    st.subheader(" Split PDF (Upload + Save to Folder)")
    uploaded_file = st.file_uploader("Choose PDF file to split", type=["pdf"])

    output_dir = st.text_input(
        "Enter output folder path (must already exist)"
        #placeholder="C:/Users/YourName/Desktop/output"
    )

    if st.button("Split PDF"):

        if uploaded_file is None:
            st.error("Please upload a PDF file.")
        elif not output_dir:
            st.error("Please enter output folder path.")
        else:
            try:
                if not os.path.exists(output_dir):
                    st.error("Output folder does not exist.")
                else:
                    file_bytes = uploaded_file.getvalue()
                    reader = PdfReader(io.BytesIO(file_bytes))

                    st.write(f"Total pages: {len(reader.pages)}")

                    for i, page in enumerate(reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)

                        output_path = os.path.join(output_dir, f"page_{i+1}.pdf")

                        with open(output_path, "wb") as f:
                            writer.write(f)

                    st.success(f"Split completed successfully! Saved in:\n{output_dir}")

            except Exception as e:
                st.error(f"Error: {str(e)}")