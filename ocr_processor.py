import os
import base64
import json
import requests
from typing import List, Dict
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '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')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def encode_image_to_base64(image_path: str) -> str:
    """Convert image to base64 string for API with quality optimization."""
    from PIL import Image, ImageEnhance, ImageFilter
    import io
    
    try:
        # Open and enhance the image for better OCR
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Scale up if image is too small (less than 2000px wide for better OCR)
            if img.width < 2000:
                scale_factor = 2000 / img.width
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Enhance contrast for better text recognition
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)  # Increase contrast by 30%
            
            # Enhance sharpness for clearer text
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.5)  # Increase sharpness by 50%
            
            # Apply a slight unsharp mask for even better text clarity
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Save as very high-quality JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=98, optimize=True, dpi=(300, 300))
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode('utf-8')
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        # Fallback to original method
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

def process_image_with_ocr(image_path: str) -> List[Dict]:
    """
    Process a single image using OpenRouter API to extract vacation/contract data.
    Returns a list of records in the same format as the PDF processor.
    """
    base64_image = encode_image_to_base64(image_path)
    
    prompt = """
You are an expert OCR system for Spanish labor documents. Analyze this "INFORME DE VIDA LABORAL - SITUACIONES" document image and extract ONLY the relevant rows.

DOCUMENT TABLE STRUCTURE:
The table has these columns from LEFT TO RIGHT:
1. RÉGIMEN (regime)
2. CÓD. EMPRESA (company code) 
3. EMPRESA (company name)
4. FECHA ALTA (start date) - THIS IS THE 4TH COLUMN
5. FECHA EFECTO ALTA (effect date) - THIS IS THE 5TH COLUMN - DO NOT USE THIS
6. FECHA DE BAJA (end date) - THIS IS THE 6TH COLUMN - USE THIS FOR fechaBaja

CRITICAL: There are TWO date columns after the company name:
- Column 4: "FECHA ALTA" - USE THIS for fechaAlta
- Column 5: "FECHA EFECTO ALTA" - IGNORE THIS COMPLETELY 
- Column 6: "FECHA DE BAJA" - USE THIS for fechaBaja

ONLY extract rows where the EMPRESA column (3rd column) contains:
1. "VACACIONES RETRIBUIDAS Y NO DISFRUTADAS" (or similar variations) - these are VACATION records
2. "SERVICIO DE SALUD DEL PRINCIPADO DE ASTURIAS" (or similar variations) - these are CONTRACT records

DATE EXTRACTION RULES:
- fechaAlta: Extract from column 4 "FECHA ALTA" (NOT from column 5!)
- fechaBaja: Extract from column 6 "FECHA DE BAJA" (the RIGHTMOST date column)
- Convert dates from DD.MM.YYYY to DD/MM/YYYY format
- Use empty string "" if no end date is present in column 6

CRITICAL: DO NOT confuse "FECHA EFECTO ALTA" (column 5) with "FECHA DE BAJA" (column 6). The end date is in the RIGHTMOST column, NOT the column immediately after FECHA ALTA.

For each relevant row:
- isVacaciones: true if company contains "VACACIONES RETRIBUIDAS Y NO", false if "SERVICIO DE SALUD"
- fechaAlta: Date from column 4 in DD/MM/YYYY format
- fechaBaja: Date from column 6 in DD/MM/YYYY format (empty string if no date)

The response will be automatically structured according to the defined JSON schema.
    """
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistralai/pixtral-large-2411",  # Mistral's vision model with OCR capabilities
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1,  # Low temperature for consistent OCR results
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "vida_laboral_simplified",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "records": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "isVacaciones": {
                                        "type": "boolean",
                                        "description": "true for vacation records, false for contract records"
                                    },
                                    "fechaAlta": {
                                        "type": "string",
                                        "description": "Start date in DD/MM/YYYY format"
                                    },
                                    "fechaBaja": {
                                        "type": "string",
                                        "description": "End date in DD/MM/YYYY format, empty string if no end date"
                                    }
                                },
                                "required": ["isVacaciones", "fechaAlta", "fechaBaja"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["records"],
                    "additionalProperties": False
                }
            }
        }
    }
    
    try:
        logger.info(f"Making API request for {image_path}...")
        logger.info(f"Environment variable set: {os.getenv('OPENROUTER_API_KEY') is not None}")
        logger.info(f"Using API key: {OPENROUTER_API_KEY[:20]}...")
        logger.info(f"Payload model: {payload['model']}")
        
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        logger.info(f"Response status: {response.status_code}")
        
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"API response keys: {list(result.keys())}")
        
        if 'choices' not in result or not result['choices']:
            logger.error(f"No choices in response: {result}")
            return []
            
        content = result['choices'][0]['message']['content']
        logger.info(f"Raw API response content: {content[:500]}...")
        
        # Parse structured JSON response
        try:
            data = json.loads(content)
            # Extract records from structured response
            records = data.get('records', [])
            logger.info(f"Successfully processed {image_path}: {len(records)} records found")
            
            # Log each extracted record for verification
            logger.info(f"--- Records from {image_path} ---")
            for i, record in enumerate(records, 1):
                vacation_type = "VACATION" if record.get('isVacaciones') else "CONTRACT"
                logger.info(f"  {i:2d}. {vacation_type:8s} | {record.get('fechaAlta', 'N/A'):10s} to {record.get('fechaBaja', 'N/A'):10s}")
            logger.info("--- End records ---")
            
            return records
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from {image_path}: {e}")
            logger.error(f"Raw content: {content}")
            # Try to extract records from non-JSON response
            if "VACACIONES" in content or "SERVICIO DE SALUD" in content:
                logger.warning("Found keywords in response, but couldn't parse JSON. Manual extraction needed.")
            return []
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error processing {image_path}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                logger.error(f"Error details: {error_details}")
            except:
                logger.error(f"Error response text: {e.response.text[:500]}...")
        return []

def process_all_images(images_dir: str = "data/imagenes") -> List[Dict]:
    """
    Process all images in the directory and combine results.
    Returns combined data in the same format as PDF processor.
    """
    if not os.path.exists(images_dir):
        print(f"Images directory {images_dir} not found")
        return []
    
    all_records = []
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    image_files.sort()  # Process in consistent order
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file in image_files:
        image_path = os.path.join(images_dir, image_file)
        print(f"Processing {image_file}...")
        
        records = process_image_with_ocr(image_path)
        all_records.extend(records)
    
    print(f"Total records extracted: {len(all_records)}")
    
    # Summary statistics
    vacation_count = sum(1 for r in all_records if r.get('isVacaciones', False))
    contract_count = len(all_records) - vacation_count
    
    print(f"\n=== EXTRACTION SUMMARY ===")
    print(f"Total vacation records: {vacation_count}")
    print(f"Total contract records: {contract_count}")
    print(f"Total records: {len(all_records)}")
    print(f"===========================\n")
    
    return all_records

def format_date_for_output(date_str: str) -> str:
    """Convert DD.MM.YYYY to DD/MM/YYYY format and validate."""
    if not date_str or date_str == "":
        return ""
    try:
        # Convert DD.MM.YYYY to DD/MM/YYYY
        formatted = date_str.replace(".", "/")
        # Validate the date format
        if len(formatted.split("/")) == 3:
            return formatted
        return date_str
    except:
        return date_str

def convert_ocr_to_extract_format(ocr_records: List[Dict]) -> List[Dict]:
    """
    OCR records are already in the final format, just normalize dates.
    """
    normalized_records = []
    for record in ocr_records:
        normalized_records.append({
            "isVacaciones": record["isVacaciones"],
            "fechaAlta": format_date_for_output(record["fechaAlta"]),
            "fechaBaja": format_date_for_output(record["fechaBaja"])
        })
    return normalized_records

if __name__ == "__main__":
    # Test the OCR processing
    records = process_all_images()
    formatted_data = convert_ocr_to_extract_format(records)
    
    print(f"\nProcessed {len(formatted_data)} relevant records")
    print(f"Vacation records: {sum(1 for r in formatted_data if r['isVacaciones'])}")
    print(f"Contract records: {sum(1 for r in formatted_data if not r['isVacaciones'])}")
    
    # Save test output
    with open("output/ocr_test_output.json", "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, ensure_ascii=False, indent=2)