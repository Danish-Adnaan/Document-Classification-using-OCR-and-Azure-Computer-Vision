import json
import csv
import re
from pathlib import Path

# Setting up paths
script_dir = Path(__file__).parent
input_json = script_dir / "output" / "ocr_result.json"
output_csv = script_dir / "output" / "extracted_fields.csv"

if not input_json.exists():
    raise FileNotFoundError(f"Input JSON file not found: {input_json}")
print(f"Input JSON file found: {input_json}")

# 1. Loading OCR JSON
with open(input_json, "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

# 2. Processing OCR Data
pages = ocr_data['analyzeResult']['readResults']
print(f"Total pages in OCR result: {len(pages)}")

# Extracting all lines of text with their bounding boxes
all_lines_data = []
all_text = ""

# Collecting all lines and text
for page_idx, page in enumerate(pages):
    for line_idx, line in enumerate(page.get('lines', [])):
        text = line.get('text', '').strip()
        bbox = line.get('boundingBox', [])
        all_lines_data.append({
            "page": page_idx + 1,
            "line": line_idx + 1,
            "text": text,
            "bounding_box": bbox
        })
        all_text += text + " "

print(f"Total lines extracted: {len(all_lines_data)}")
print(f"Total characters in all text: {len(all_text)}")


# 3. Extracting Specific Fields
fields = {
    "Form Tracking Number" : {
        "header_regex" : r"form\s+tracking\s+number|Form\s+Tracking\s+Number",
        "value_regex" : r"TRK-[A-Z0-9]{10,15}",
        "description" : "Alphanumeric code starting with TRK-"
    },
    "Part Number" : {
        "header_regex" : r"part\s+number|Part\s+Number|^\s*8\s+Part|PN-",
        "value_regex" : r"PN-[A-Z0-9]{6,12}",
        "description" : "Part Code in format PN-XXXXX"
    },
    "Serial Number" : {
        "header_regex" : r"serial\s+no|Serial\s+No|^\s*10\s+Serial|SN-",
        "value_regex" : r"SN-[A-Z0-9]{6,12}",
        "description" : "Serial Number in format SN-XXXXX"
    },

    "Date" : {
        "header_regex" : r"date|Date|13a|13b",
        "value_regex" : r"\b\d{1,2}\s+[A-Z]{3,4}\s+\d{4}\b|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}",
        "description" : "Date in formats like DD MMM YYYY or 12/03/2023"
    }

}

# Initializing results dictionary
results = {
    "Form Tracking Number": "",
    "Part Number": "",
    "Serial Number": "",
    "Date": ""
}

print("Extracting fields from OCR text..")


# Searching for each field 
for field_name, config in fields.items():
    print(f"Searching for field: {field_name}")

    found = False

    for i,line_data in enumerate(all_lines_data):
        text = line_data['text']

        if re.search(config['header_regex'], text, re.IGNORECASE):
            print(f"  Found header in line: {text}")

            value_match = re.search(config['value_regex'], text)
            if value_match:
                value = value_match.group(0)
                results[field_name] = value
                print(f" Found value in same line: {value}")
                found = True
                break

            if i + 1 < len(all_lines_data):
                next_text = all_lines_data[i + 1]['text']
                value_match = re.search(config['value_regex'], next_text)
                if value_match:
                    value = value_match.group(0)
                    results[field_name] = value
                    print(f" Found value in next line: {value}")
                    found = True
                    break

            if i+2 < len(all_lines_data):
                next2_text = all_lines_data[i + 2]['text']
                value_match = re.search(config['value_regex'], next2_text)
                if value_match:
                    value = value_match.group(0)
                    results[field_name] = value
                    print(f" Found value in line after next: {value}")
                    found = True
                    break
    if not found:
        print(f" Header not found, searching for pattern directly...")
        value_match = re.search(config['value_regex'], all_text)
        if value_match:
            value = value_match.group(0)
            results[field_name] = value
            print(f" Found value directly in text: {value}")
        else:
            print(f" Could not find value for field: {field_name}")

    print()


print ("Writing CSV file with extracted fields...")

# 4. Writing results to CSV
output_csv.parent.mkdir(parents=True, exist_ok=True)

with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Form Tracking Number", "Part Number", "Serial Number", "Date"])

    writer.writerow([
        results["Form Tracking Number"],
        results["Part Number"],
        results["Serial Number"],
        results["Date"]
    ])

print(f"Extracted fields saved to CSV: {output_csv}")
print(f"   {results['Form Tracking Number']}, {results['Part Number']}, {results['Serial Number']}, {results['Date']}\n")

