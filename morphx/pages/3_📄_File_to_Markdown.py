from PIL import Image

import streamlit as st
import fitz
import pytesseract
import numpy as np
from markdownify import markdownify as md
from markitdown import MarkItDown
from pypdf import PdfReader


# Set the page configuration for Streamlit
st.set_page_config(page_title="PDF2MD", page_icon="📄", layout="wide")
st.title("📄 File to Markdown")
st.sidebar.image("./images/logo.png")


def extract_text_from_pdf_ocr(pdf_file, ln: str) -> str or None:
    """
    Extract text from a PDF file using OCR.

    Args:
        pdf_file (BytesIO): The PDF file object.

    Returns:
        str: The extracted text from the PDF, or None if there was an error.
    """

    try:

        # Open the PDF file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""

        for page_num in range(len(pdf_document)):

            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()

            # Save the page image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Apply image preprocessing
            img = preprocess_image(img)

            # Apply OCR to the image
            page_text = pytesseract.image_to_string(img, lang=ln)
            text += page_text + "\n"

        return text

    except Exception as e:

        st.error(f"Error extracting text from PDF using OCR: {e}")
        return None


def extract_text_from_pdf_pypdf2(pdf_file) -> str or None:
    """
    Extract text from a PDF file using PyPDF2.

    Args:
        pdf_file (BytesIO): The PDF file object.

    Returns:
        str: The extracted text from the PDF, or None if there was an error.
    """

    try:

        # Open the PDF file
        pdf_reader = PdfReader(pdf_file)  # Updated to PdfReader
        text = ""

        for page in pdf_reader.pages:

            text += page.extract_text() + "\n"

        return text

    except Exception as e:

        st.error(f"Error extracting text from PDF using PyPDF2: {e}")
        return None


def extract_text_from_pdf_ctrl_a(pdf_file) -> str or None:
    """
    Extract text from a PDF file by emulating Ctrl+A.

    Args:
        pdf_file (BytesIO): The PDF file object.

    Returns:
        str: The extracted text from the PDF, or None if there was an error.
    """

    try:

        # Open the PDF file
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""

        for page in pdf_document:

            text += page.get_text() + "\n"  # Updated to get_text()

        return text

    except Exception as e:

        st.error(f"Error extracting text from PDF using Ctrl+A: {e}")
        return None


def convert_text_to_markdown(text: str) -> str:
    """
    Convert plain text to Markdown format.

    Args:
        text (str): The plain text to convert.

    Returns:
        str: The converted Markdown text.
    """

    markdown_text = md(text)
    return markdown_text


def main() -> None:
    """
    Run the Streamlit app to convert a PDF file to Markdown.
    """

    col1, col2 = st.columns(2)
    extraction_method = "MarkItDown"
    uploaded_file = None

    with col1:

        st.subheader("File configuration")

        if extraction_method != "MarkItDown":
            uploaded_file = st.file_uploader("Upload a file")
        else:
            uploaded_file_path = st.text_input("Introduce the path of the file")

        output_path = st.text_input("Enter the output directory", ".")
        output_file = st.text_input("Enter the output file name", "output")
        output_file = f"{output_path}/{output_file}.md"

    with col2:

        st.subheader("Method configuration")

        st.info(
            """
            + PyPDF method may not work well with scanned PDFs or PDFs with complex layouts.
            + Ctrl+A method may not work well with PDFs that contain a lot of graphics or tables. 
            + The OCR method is generally the most accurate, but it can be slow and may not work well with PDFs that contain a lot of noise or distortion.
            + MarkItDown
            """
        )

        extraction_method = st.selectbox(
            "Select the extraction method", ["OCR", "PyPDF", "Ctrl+A", "MarkItDown"],
            index=3,
        )

        if extraction_method == "OCR":

            ln = st.multiselect(
                "List of available languages", pytesseract.get_languages(), ["eng"]
            )
            ln = "+".join(ln)

    if ((uploaded_file is not None) or (uploaded_file_path is not None)) and (st.button("Extract text")):

        if extraction_method == "OCR":

            with st.spinner("Applying OCR to the document..."):

                text = extract_text_from_pdf_ocr(uploaded_file, ln)

        elif extraction_method == "PyPDF":

            text = extract_text_from_pdf_pypdf2(uploaded_file)

        elif extraction_method == "Ctrl+A":

            text = extract_text_from_pdf_ctrl_a(uploaded_file)

        elif extraction_method == "MarkItDown":

            md = MarkItDown()
            text = md.convert(uploaded_file_path)

        else:

            st.error(f"Option not available.")
            return None

        if text and extraction_method != "MarkItDown":

            text = convert_text_to_markdown(text)

            st.subheader("Extracted text")
            st.text_area("Extracted Text", text, height=300, label_visibility="hidden")

        save_button = st.button("Save as .md")

        if save_button:

            with open(output_file, "w", encoding="utf-8") as f:

                f.write(text)

            st.success(f"File saved as {output_file}")

        else:

            st.error(f"An error has occurred during text extraction, please try again.")
            return None


if __name__ == "__main__":

    main()
