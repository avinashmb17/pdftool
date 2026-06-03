import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import zipfile

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
# MERGE MODE (FULL CONTROL)
# =========================================================
if st.session_state.mode == "merge":

    #st.subheader("🔀 Merge PDFs (Reorder Pages)")
    st.subheader(" Merge PDFs (Reorder Pages)")

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
                        {
                            "name": file.name,
                            "bytes": file_bytes,
                            "page": i
                        }
                    )

            st.success("Pages loaded successfully!")

    # ---------------- SHOW PAGES ----------------
    st.write("### Current Page Order")

    if st.session_state.pages:

        page_labels = [
            f"{i+1}. {p['name']} - Page {p['page']+1}"
            for i, p in enumerate(st.session_state.pages)
        ]

        st.dataframe(page_labels, use_container_width=True)

        # ---------------- SELECT PAGE ----------------
        selected_index = st.selectbox(
            "Select page to move",
            list(range(len(st.session_state.pages))),
            format_func=lambda i: page_labels[i]
        )

        col1, col2, col3 = st.columns(3)

        # MOVE UP
        with col1:
            if st.button("⬆ Move Up"):
                i = selected_index
                if i > 0:
                    st.session_state.pages[i], st.session_state.pages[i - 1] = (
                        st.session_state.pages[i - 1],
                        st.session_state.pages[i]
                    )
                    st.rerun()

        # MOVE DOWN
        with col2:
            if st.button("⬇ Move Down"):
                i = selected_index
                if i < len(st.session_state.pages) - 1:
                    st.session_state.pages[i], st.session_state.pages[i + 1] = (
                        st.session_state.pages[i + 1],
                        st.session_state.pages[i]
                    )
                    st.rerun()

        # MOVE TO POSITION
        with col3:
            new_pos = st.number_input(
                "Move to position",
                min_value=1,
                max_value=len(st.session_state.pages),
                value=selected_index + 1
            )

            #if st.button("📍 Move to Position"):
            if st.button(" Move to Position"):
                i = selected_index
                item = st.session_state.pages.pop(i)
                st.session_state.pages.insert(new_pos - 1, item)
                st.rerun()

    else:
        st.info("Upload PDFs and click 'Load Pages'")

    # ---------------- MERGE PDF ----------------
    if st.button("Merge PDFs"):

        if not st.session_state.pages:
            st.warning("No pages selected.")
        else:
            writer = PdfWriter()

            for p in st.session_state.pages:
                reader = PdfReader(io.BytesIO(p["bytes"]))
                writer.add_page(reader.pages[p["page"]])

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
# SPLIT MODE (ZIP DOWNLOAD)
# =========================================================
else:

    #st.subheader("✂️ Split PDF (Download as ZIP)")
    st.subheader(" Split PDF (Download as ZIP)")
    uploaded_file = st.file_uploader(
        "Choose PDF file to split",
        type=["pdf"]
    )

    if st.button("Split PDF"):

        if uploaded_file is None:
            st.error("Please upload a PDF file.")
        else:
            try:
                file_bytes = uploaded_file.getvalue()
                reader = PdfReader(io.BytesIO(file_bytes))

                st.write(f"Total pages: {len(reader.pages)}")

                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

                    for i, page in enumerate(reader.pages):
                        writer = PdfWriter()
                        writer.add_page(page)

                        pdf_buffer = io.BytesIO()
                        writer.write(pdf_buffer)
                        pdf_buffer.seek(0)

                        zip_file.writestr(
                            f"page_{i+1}.pdf",
                            pdf_buffer.read()
                        )

                zip_buffer.seek(0)

                st.success("PDF split successfully!")

                st.download_button(
                    "Download Split PDFs (ZIP)",
                    data=zip_buffer,
                    file_name="split_pages.zip",
                    mime="application/zip"
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")
