import google.generativeai as genai
import json
import logging
import traceback
import mimetypes
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Mistral setup
mistral_client = None
if hasattr(settings, 'MISTRAL_API_KEY') and settings.MISTRAL_API_KEY:
    try:
        from mistralai.client import Mistral
        mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)
    except ImportError:
        logger.error("mistralai is not installed.")

PROMPT = """
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

def extract_with_gemini(mime_type: str, file_bytes: bytes) -> tuple[dict | None, float | None]:
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    logger.info("OCR Provider: Gemini")
    model = genai.GenerativeModel('gemini-1.5-flash')
    image_part = {
        "mime_type": mime_type,
        "data": file_bytes
    }
    
    response = model.generate_content([image_part, PROMPT])
    text = response.text.strip()
    
    if text.startswith("```json"):
        text = text[7:-3].strip()
    elif text.startswith("```"):
        text = text[3:-3].strip()
        
    data = json.loads(text)
    return data, 0.95

def extract_with_mistral(file_path: str, file_bytes: bytes) -> tuple[dict | None, float | None]:
    if not mistral_client:
        raise ValueError("Mistral client is not initialized or API key is missing.")

    logger.info("OCR Provider: Mistral")
    
    # 1. Upload to Mistral for OCR
    uploaded_file = mistral_client.files.upload(
        file={"file_name": os.path.basename(file_path), "content": file_bytes},
        purpose="ocr"
    )
    
    try:
        signed_url = mistral_client.files.get_signed_url(file_id=uploaded_file.id)
        
        # 2. Extract Text via Mistral OCR
        ocr_response = mistral_client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url
            }
        )
        
        raw_text = "\n".join([page.markdown for page in ocr_response.pages])
        
        # 3. Parse JSON via Mistral Large
        chat_response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "user", "content": f"{PROMPT}\n\nDocument OCR Text:\n{raw_text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        text = chat_response.choices[0].message.content.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        data = json.loads(text)
        return data, 0.95
        
    finally:
        # Always cleanup the file from Mistral
        try:
            mistral_client.files.delete(file_id=uploaded_file.id)
        except Exception as e:
            logger.warning(f"Failed to delete file from Mistral: {e}")

def extract_invoice_data(file_path: str) -> tuple[dict | None, float | None]:
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/pdf"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        logger.info(f"OCR Processing: {file_path} ({mime_type})")
        
        try:
            return extract_with_gemini(mime_type, file_bytes)
        except json.JSONDecodeError as e:
            logger.error(f"Gemini parsed invalid JSON: {e}. Not falling back for parsing bugs.")
            return None, None
        except Exception as e:
            # Fallback on API limits, quota exceeded, or generic API failures
            logger.error(f"Gemini OCR failed: {e}")
            logger.info("Switching to Mistral OCR.")
            return extract_with_mistral(file_path, file_bytes)
            
    except json.JSONDecodeError as e:
        logger.error(f"Mistral parsed invalid JSON: {e}")
        return None, None
    except Exception as e:
        logger.error(f"OCR Exception: {e}")
        traceback.print_exc()
        return None, None
