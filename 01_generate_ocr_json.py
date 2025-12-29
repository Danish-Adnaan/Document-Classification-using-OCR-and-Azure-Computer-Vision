import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Loading the Azure Credentials
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")

#making sure output directory exists
script_dir = Path(__file__).parent
input_dir = script_dir / "input" / "input.pdf"
output_dir = script_dir / "output"
output_json_path = output_dir / "ocr_result.json"
output_dir.mkdir(parents=True, exist_ok=True)

if not input_dir.exists():
    raise FileNotFoundError(f"Input file not found: {input_dir}")

print(f"input PDF found: {input_dir}")

# Reading the PDF file
print ("Running OCR on the document...")
with open(input_dir, "rb") as pdf_file:
    pdf_data = pdf_file.read()
print(f"PDF file loaded successfully ({len(pdf_data) / 1024:.2f} KB).")

ocr_url = f"{AZURE_ENDPOINT}/vision/v3.2/read/analyzeResults"
ocr_submit_url = f"{AZURE_ENDPOINT}/vision/v3.2/read/analyze"

# Setting up headers and parameters for the OCR request
headers = {
    "Ocp-Apim-Subscription-Key": AZURE_API_KEY,
    "Content-Type": "application/octet-stream"
}

print("Submitting OCR request to Azure...")

# Submitting OCR request
try:
    response = requests.post(ocr_submit_url, headers=headers, data=pdf_data, timeout = 30)
    response.raise_for_status()

    print("OCR request submitted successfully.")

    operation_url = response.headers.get("Operation-Location")
    if not operation_url:
        raise Exception("Operation-Location header not found in the response.")
    print(f"Operation URL: {operation_url}")

except requests.exceptions.RequestException as e:
    print(f"Error submitting OCR request: {e}")
    raise

print("Polling for OCR result status")

max_retries = 10
retry_delay = 2
attempt = 0
ocr_result = None

# Polling for result
while attempt < max_retries:
    attempt += 1
    try:
        poll_response = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": AZURE_API_KEY}, timeout = 10)
        poll_result = poll_response.json()
        status = poll_result.get("status" , "unknown")

        print(f"Attempt {attempt}: OCR status - {status}")

        if status == "succeeded":
            ocr_result = poll_result
            print("OCR processing succeeded.")
            break

        elif status == "failed":
            print("OCR processing failed.")
            break

    except requests.exceptions.RequestException as e:
        print(f"Error polling and parsing OCR result: {e}")

if ocr_result is None or ocr_result.get("status") != "succeeded":
    raise Exception("OCR processing did not complete successfully.")

print(f"Saving OCR result to JSON file")

# Saving OCR result to JSON file
try:
    json_output = json.dumps(ocr_result, indent=2)

    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json_file.write(json_output)

    print(f"OCR result saved to {output_json_path}")

except IOError as e:
    print(f"Error saving OCR result to JSON file: {e}")


#Extracting key information from OCR result
pages = ocr_result.get("analyzeResult", {}).get("readResults", [])
total_pages = len(pages)
total_lines = sum(len(page.get("lines", [])) for page in pages)
total_words = sum(len(line.get("words", [])) for page in pages for line in page.get("lines", []))

print(f"Total Pages: {total_pages}")
print(f"Total Lines: {total_lines}")
print(f"Total Words: {total_words}")

if total_lines>0:
    sample_line = pages[0].get("lines", [])[0]
    print(f"Sample Line Text: {sample_line.get('text', '')}")
    print(f"Sample Line Bounding Box: {sample_line.get('boundingBox', [])}")

