## Azure Setup

1. Create free Azure account: https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account?icid=ai-vision
2. Azure Portal → Create Resource → "Computer Vision" →  (Configurations - Region = SOutheast Asia) etc -> use Free F0 tier
3. Copy ENDPOINT and KEY from "Keys and Endpoint"
4. Create `.env` file: and store them as 
-- AZURE_ENDPOINT=https://<region>.api.cognitive.microsoft.com/
-- AZURE_KEY=<your-key>

## Required Libraries

pip install azure-cognitiveservices-vision-computervision python-dotenv PyMuPDF pandas requests

## Usage

### Script 1: Generate OCR JSON
To run paste this in terminal : python 01_generate_ocr_json.py 

**Output:** `output/ocr_result.json`


### Script 2: Extract Fields to CSV
To run paste this in terminal : python 02_extract_fields_to_csv.py 

**Output:** `output/extracted_fields.csv`

### Script 3: Annotate PDF
To run paste this in terminal : python 03_annotate_pdf.py 

**Output:** `output/annotated.pdf`

## Expected CSV Format
Form Tracking Number,Part Number,Serial No.,Date
TRK-3MNM9VYW52,PN-C2P417IW,SN-QTDGGM,31 OCT 2025