import google.generativeai as genai
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_invoice_data(file_path: str) -> tuple[dict | None, float | None]:
    """
    Calls Gemini Vision API to extract structured invoice data from a file.
    Returns a tuple of (extracted_data_dict, confidence_score).
    If OCR fails, returns (None, None).
    """
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured.")
        return None, None

    try:
        logger.info(f"Uploading file for OCR: {file_path}")
        # Upload the file using the Gemini API
        sample_file = genai.upload_file(path=file_path)
        
        # Use gemini-1.5-flash which is ideal for multimodal extraction tasks
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        Extract the following information from this invoice document.
        You must return ONLY a valid JSON object. Do not include markdown code blocks (e.g. ```json). Do not include any extra text.
        Required structure:
        {
            "invoice_number": "string",
            "vendor_name": "string",
            "gstin": "string",
            "invoice_date": "string (format YYYY-MM-DD)",
            "subtotal": number,
            "gst_amount": number,
            "total_amount": number,
            "line_items": [
                {
                    "description": "string",
                    "quantity": number,
                    "unit_price": number,
                    "line_total": number
                }
            ]
        }
        If a field is not found, use null. For numbers, do not include currency symbols or commas.
        """
        
        logger.info("Calling Gemini API...")
        response = model.generate_content([sample_file, prompt])
        
        text = response.text.strip()
        # Clean up any potential markdown formatting if the model still includes it
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        
        # As Gemini API doesn't return an explicit confidence score for generative tasks in the same way 
        # some traditional OCR systems do, we'll provide a reasonable default as per requirements.
        # TODO: Replace with actual confidence scoring from Gemini API when available.
        confidence = 0.95
        
        # Cleanup the file from Gemini storage
        try:
            genai.delete_file(sample_file.name)
        except Exception as e:
            logger.warning(f"Failed to delete file from Gemini storage: {e}")
            
        return data, confidence
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from Gemini response: {e}")
        logger.error(f"Raw response was: {text}")
        return None, None
    except Exception as e:
        logger.error(f"OCR Exception: {e}")
        return None, None
