import os
import shutil

import streamlit as st
import pikepdf
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from faker import Faker
from stqdm import stqdm

# Generate random data for metadata
fake = Faker()


# Set the page configuration for Streamlit
st.set_page_config(page_title="Metadata", page_icon="📝")
st.title("📝 Metadata")
st.sidebar.image("./images/logo.png")


def create_cover(file_name: str, degree_name: str, output_path: str) -> None:
    """
    Create a cover page for the PDF with the file name and degree name.

    Args:
        file_name (str): The name of the file to display on the cover.
        degree_name (str): The name of the degree to display on the cover.
        output_path (str): The path where the cover PDF will be saved.
    """

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Write the file name on the cover
    c.setFont("Helvetica", 24)
    c.drawCentredString(width / 2.0, height / 2.0 + 40, f"File Name: {file_name}")

    # Write the degree name on the cover
    c.setFont("Helvetica", 20)
    c.drawCentredString(width / 2.0, height / 2.0, f"Degree: {degree_name}")

    c.save()


def modify_metadata_and_add_cover(
    pdf_path: str, degree_name: str, output_path: str
) -> None:
    """
    Modify the metadata and add a cover page to the PDF.

    Args:
        pdf_path (str): The path to the original PDF.
        degree_name (str): The name of the degree to display on the cover.
        output_path (str): The path where the modified PDF will be saved.
    """

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Create a temporary cover in the same directory as the PDF
    cover_path = os.path.join(os.path.dirname(output_path), "cover_temp.pdf")
    create_cover(os.path.basename(pdf_path), degree_name, cover_path)

    # Read the cover and add it
    cover_reader = PdfReader(cover_path)
    writer.add_page(cover_reader.pages[0])

    # Add the original PDF pages
    for page in reader.pages:

        writer.add_page(page)

    # Random metadata
    metadata = {
        "/Title": fake.sentence(nb_words=5),
        "/Author": fake.name(),
        "/Subject": fake.sentence(nb_words=7),
        "/Producer": fake.company(),
        "/Creator": fake.name(),
        "/Keywords": ", ".join(fake.words(nb=5)),
    }

    writer.add_metadata(metadata)

    # Save the file with modified metadata and added cover
    temp_output_path = output_path + ".temp"

    with open(temp_output_path, "wb") as modified_file:

        writer.write(modified_file)

    # Remove the temporary cover file
    os.remove(cover_path)

    # Compress the PDF
    with pikepdf.open(temp_output_path) as pdf:

        pdf.save(output_path)

    # Remove the temporary uncompressed file
    os.remove(temp_output_path)


def analyze_directory(
    original_directory: str, new_directory: str, degree_name: str
) -> None:
    """
    Analyze the directory, modify PDF metadata, and add a cover page.

    Args:
        original_directory (str): The path to the original directory.
        new_directory (str): The path to the new directory.
        degree_name (str): The name of the degree to display on the cover.
    """

    for root, dirs, files in os.walk(original_directory):

        # Create the directory structure in the new directory
        relative_path = os.path.relpath(root, original_directory)
        new_root = os.path.join(new_directory, relative_path)
        os.makedirs(new_root, exist_ok=True)

        for _ in stqdm(range(len(files)), desc="Making the modifications..."):

            for file in files:

                if file.lower().endswith(".pdf"):

                    pdf_path = os.path.join(root, file)
                    new_pdf_path = os.path.join(new_root, file)
                    modify_metadata_and_add_cover(pdf_path, degree_name, new_pdf_path)
                    print(f"Metadata and cover modified for {new_pdf_path}")

                else:

                    # Copy other files without modifications
                    shutil.copy(os.path.join(root, file), os.path.join(new_root, file))


def main() -> None:

    data_directory = st.text_input("Enter the document directory")
    output_directory = st.text_input("Enter the document directory for the output")

    degree = st.selectbox(
        "Possible grades",
        (
            "Bachelor in Electronic Systems Engineering",
            "Bachelor in Telecommunication Systems Engineering",
            "Bachelor in Sound and Image Engineering",
            "Bachelor in Telecommunication Technologies Engineering",
            "Bachelor in Telematics Engineering",
            "Double Degree in Telecommunication Technologies Engineering and Mathematics",
            "Others",
        ),
    )

    if degree == "Others":

        degree = st.text_input("Enter the name of the degree:")

    start_button = st.button("Initialize metadata modification")

    if start_button:

        new_directory = f"./{output_directory}/{degree}/"
        os.makedirs(new_directory, exist_ok=True)
        analyze_directory(data_directory, new_directory, degree)


if __name__ == "__main__":

    main()
