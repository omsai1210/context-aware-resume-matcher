import fitz  # PyMuPDF
from docx import Document
import io
import re

def clean_text(text: str) -> str:
    """
    Cleans the extracted text by normalizing whitespace and line breaks.
    
    Args:
        text (str): The raw extracted text.
        
    Returns:
        str: The cleaned text.
    """
    if not text:
        return ""
    # Replace multiple newlines with a single newline
    text = re.sub(r'[\r\n]+', '\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_text_from_pdf(content: bytes) -> str:
    """
    Extracts text from a PDF file's byte content.
    
    Args:
        content (bytes): The raw bytes of the PDF file.
        
    Returns:
        str: The extracted and cleaned text.
        
    Raises:
        ValueError: If text cannot be extracted or the file is corrupted.
    """
    try:
        # Open the PDF from bytes
        doc = fitz.open(stream=content, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        
        extracted_text = "\n".join(text_parts)
        if not extracted_text.strip():
            raise ValueError("No extractable text found in the PDF. It might be a scanned image or corrupted.")
            
        return clean_text(extracted_text)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")

def extract_text_from_docx(content: bytes) -> str:
    """
    Extracts text from a DOCX file's byte content.
    
    Args:
        content (bytes): The raw bytes of the DOCX file.
        
    Returns:
        str: The extracted and cleaned text.
        
    Raises:
        ValueError: If text cannot be extracted or the file is corrupted.
    """
    try:
        # docx needs a file-like object
        file_stream = io.BytesIO(content)
        doc = Document(file_stream)
        text_parts = [para.text for para in doc.paragraphs]
        extracted_text = "\n".join(text_parts)
        
        if not extracted_text.strip():
             raise ValueError("No extractable text found in the DOCX. It might be empty or corrupted.")
             
        return clean_text(extracted_text)
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {str(e)}")

def extract_text_from_txt(content: bytes) -> str:
    """
    Extracts text from a TXT file's byte content.
    
    Args:
        content (bytes): The raw bytes of the TXT file.
        
    Returns:
        str: The extracted and cleaned text.
        
    Raises:
        ValueError: If the file cannot be decoded.
    """
    try:
        # Try utf-8 first, fallback to common encodings if needed
        try:
             extracted_text = content.decode('utf-8')
        except UnicodeDecodeError:
             extracted_text = content.decode('latin-1')
             
        if not extracted_text.strip():
            raise ValueError("The TXT file is empty.")
            
        return clean_text(extracted_text)
    except Exception as e:
        raise ValueError(f"Failed to parse TXT: {str(e)}")
