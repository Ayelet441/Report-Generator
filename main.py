import os
from parsing.classifier import ReportClassifier
from parsing.type_a_parser import TypeAParser
from parsing.type_b_parser import TypeBParser
from transformation.type_a_transformation import TypeATransformationStrategy
from transformation.type_b_transformation import TypeBTransformationStrategy
from generation.renderer_factory import RendererFactory
from repositories.pdf_repository import PdfRepository  # או המחלקה הקיימת אצלך לשליפת טקסט מקובץ


def main():
    # Default configurations based on project structure
    input_path = "resources/a_r_25.pdf"  # [cite: 3]
    output_path = "output_searchable.pdf"  # [cite: 3]

    print(f"Starting pipeline processing for input file: {input_path}")

    # Ensure the output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Step 0: Extract raw text and automatically classify the report type
    print("Step 0: Extracting text and detecting report type automatically...")
    # Step 0: Extracting text and detecting report type...
    raw_text = PdfRepository.extract_text(input_path)
    print("--- DEBUG RAW TEXT START ---")
    print(raw_text[:1000])  # מדפיס את אלף התווים הראשונים
    print("--- DEBUG RAW TEXT END ---")
    # שליפת הטקסט הגולמי מהקובץ באמצעות הריפוזיטורי (יש לוודא את שם המתודה המדויק אצלך, למשל extract_text או get_text)
    raw_text = PdfRepository.extract_text(input_path)

    # יצירת מופע של הקלאסיפייר והעברת הטקסט הגולמי
    classifier = ReportClassifier()
    detected_type = classifier.classify(raw_text)

    normalized_type = detected_type.upper()
    print(f"Detected report type: {normalized_type}")

    # Step 1: Select parser and transformation strategy according to report type
    if normalized_type == "TYPE_A":
        parser = TypeAParser()
        strategy = TypeATransformationStrategy()
    elif normalized_type == "TYPE_B":
        parser = TypeBParser()
        strategy = TypeBTransformationStrategy()
    else:
        raise ValueError(f"Unsupported or unknown detected report type: '{detected_type}'")

    # Execute parsing on raw input data from the file
    # Step 1: Parsing raw data...
    print("Step 1: Parsing raw data...")
    parsed_report = parser.parse(input_path)
    print(f"DEBUG: Parsed rows count = {len(parsed_report.rows)}")
    for r in parsed_report.rows:
        print(r)
    print("Step 1 completed successfully.")

    # Step 2: Generate synthetic variation using the transformation layer
    print("Step 2: Running transformation strategy to generate synthetic data...")
    synthetic_report = strategy.transform(parsed_report)
    print("Step 2 completed successfully.")

    # Step 3: Render the transformed report to a final PDF file via RendererFactory
    print("Step 3: Generating final PDF file via Renderer...")
    renderer = RendererFactory.get_renderer(normalized_type, output_format="pdf")
    renderer.render(synthetic_report, output_path)
    print(f"Step 3 completed successfully! PDF file created at: {output_path}")


if __name__ == "__main__":
    main()