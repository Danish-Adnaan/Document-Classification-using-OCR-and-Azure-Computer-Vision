import json
import csv
import fitz
from pathlib import Path


script_dir = Path(__file__).parent
input_pdf = script_dir / "input" / "input.pdf"
input_json = script_dir / "output" / "ocr_result.json"
input_csv = script_dir / "output" / "extracted_fields.csv"
output_pdf = script_dir / "output" / "annotated_output.pdf"


#Checking all inputs exist
for file_path, file_type in [(input_pdf, "PDF"), (input_json, " OCR JSON"), (input_csv, "CSV")]:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    print(f"All input files found: {file_path} ({file_type})")  

# 1. Loading OCR JSON
with open(input_json, "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

ocr_pages = ocr_data['analyzeResult']['readResults']
print(f"Total pages in OCR result: {len(ocr_pages)}")


# 2. Load CSV
extracted_fields = []
with open(input_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        extracted_fields = {k: v for k, v in row.items() if v}

for field, value in extracted_fields.items():
    print(f"Extracted field - {field}: {value}")


#3. Load PDF
pdf_doc = fitz.open(input_pdf)
print(f"Loaded PDF with {pdf_doc.page_count} pages.")


def inches_to_points(inches):
    return inches * 72  # 1 inch = 72 

def get_field_bounding_boxes(field_value, ocr_pages):
    results = []

    if not field_value:
        return results
    for page_idx, page in enumerate(ocr_pages):
        page_height = page.get('height', 11.6806)

        for line in page.get('lines', []):
            line_text = line.get('text', '').strip()

            if field_value.upper() in line_text.upper():
                bbox = line.get('boundingBox', [])
                if len(bbox) == 8:

                    xs = [bbox[0], bbox[2], bbox[4], bbox[6]]
                    ys = [bbox[1], bbox[3], bbox[5], bbox[7]]

                    x0_inch = min(xs)
                    y0_inch = min(ys)
                    x1_inch = max(xs)
                    y1_inch = max(ys)

                    x0 = inches_to_points(x0_inch)
                    y0 = inches_to_points(y0_inch)
                    x1 = inches_to_points(x1_inch)
                    y1 = inches_to_points(y1_inch)

                    results.append({
                        "page_index": page_idx,
                        "bbox": (x0, y0, x1, y1),
                        'text': line_text,
                        'bbox_raw' : bbox
                    })
    return results


#4. Annotate PDF
COLORS = {
    "Form Tracking Number": (1, 0, 0),  # Red
    "Part Number": (0 , 0 , 1),         # Blue
    "Serial Number": (0, 1, 0),         # Green
    "Date": (0.5, 0, 0.5)               # purple
}

annotation_count = 0

# Annotating fields on PDF
for field_name, field_value in extracted_fields.items():
    if not field_value:
        print(f" Field {field_name} has no extracted value, skipping annotation.")
        continue

    print(f"Annotating field {field_name:25s} with value {field_value}")

    occurrences = get_field_bounding_boxes(field_value, ocr_pages)
    
    if not occurrences:
        print(f"  No occurrences found for value '{field_value}' in OCR data.")
        continue

    color = COLORS.get(field_name, (1, 0, 0))  # Default to red if not found


    # Annotating each occurrence
    for occurrence in occurrences:
        page_num = occurrence['page_index']
        bbox = occurrence['bbox']
        text = occurrence['text']

        pdf_page = pdf_doc[page_num]

        rect = fitz.Rect(bbox)

        # Transparent outline fill
        pdf_page.draw_rect(rect, color=color, width=2, fill=None)

        print(f"  Annotated on page {page_num + 1} at {bbox} for text '{text}'")
        annotation_count += 1

if annotation_count == 0:
    print("No annotations were made to the PDF.")

# Saving annotated PDF
output_pdf.parent.mkdir(parents=True, exist_ok=True)
pdf_doc.save(output_pdf)
pdf_doc.close()

print(f"Annotated PDF saved to: {output_pdf} with {annotation_count} annotations.")




