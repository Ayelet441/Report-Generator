import os
import pytesseract
from pdf2image import convert_from_path

# Configure Tesseract OCR engine path on the system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class PdfRepository:
    """
    Repository responsible for reading PDF files, converting full pages into images,
    running OCR using Tesseract, and extracting text for the classification system.
    """

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        # Check if the target PDF file exists before processing
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found at path: {pdf_path}")

        extracted_text = ""

        try:
            # Specify the explicit path to the Poppler bin folder on your machine
            poppler_bin_path = r"C:\Program Files\poppler-26.09.0\Library\bin"

            # Convert PDF pages into image objects
            images = convert_from_path(pdf_path, poppler_path=poppler_bin_path)

            for image in images:
                # Convert image to grayscale to improve OCR recognition accuracy
                gray_image = image.convert('L')

                # Advanced configuration for forms and structured text: --oem 1 (LSTM engine) and --psm 6 (assume a single uniform block of text)
                custom_config = r'--oem 1 --psm 6'
                scanned_text = pytesseract.image_to_string(gray_image, lang='heb+eng', config=custom_config)

                if scanned_text:
                    extracted_text += scanned_text + "\n"

        except Exception as e:
            raise RuntimeError(f"An error occurred during full-page OCR processing for file {pdf_path}: {e}")

        return extracted_text