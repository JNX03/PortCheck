"""
PDF Processing Service
Handles text extraction from PDFs with OCR fallback for image-based PDFs
"""

import logging
from pathlib import Path
from typing import Dict, List
import tempfile
import os

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction with OCR fallback"""

    def __init__(self):
        """Initialize PDF processor"""
        self.min_text_threshold = 100  # Minimum characters to consider extraction successful

    def extract_text(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF, using OCR if necessary

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dict with:
                - text: Extracted text
                - method: Extraction method used ('direct' or 'ocr')
                - pages: Number of pages processed
                - success: Whether extraction was successful
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Extracting text from: {pdf_path}")

        # Try direct text extraction first
        try:
            result = self._extract_text_direct(pdf_path)
            if result["text"] and len(result["text"].strip()) >= self.min_text_threshold:
                logger.info(f"Successfully extracted text directly ({len(result['text'])} chars)")
                return result
            else:
                logger.info(f"Direct extraction yielded insufficient text ({len(result['text'])} chars), trying OCR...")
        except Exception as e:
            logger.warning(f"Direct text extraction failed: {e}, trying OCR...")

        # Fallback to OCR
        try:
            result = self._extract_text_ocr(pdf_path)
            logger.info(f"Successfully extracted text via OCR ({len(result['text'])} chars)")
            return result
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise Exception(f"Could not extract text from PDF using any method: {e}")

    def _extract_text_direct(self, pdf_path: Path) -> Dict:
        """
        Extract text directly from PDF (for text-based PDFs)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with extraction results
        """
        if PdfReader is None:
            raise ImportError("PyPDF2 is not installed")

        try:
            reader = PdfReader(str(pdf_path))
            text_parts = []
            pages = len(reader.pages)

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Could not extract text from page {page_num}: {e}")

            full_text = "\n\n".join(text_parts)

            return {
                "text": full_text,
                "method": "direct",
                "pages": pages,
                "success": True
            }

        except Exception as e:
            logger.error(f"Direct extraction error: {e}")
            raise

    def _extract_text_ocr(self, pdf_path: Path) -> Dict:
        """
        Extract text using OCR (for image-based PDFs)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with extraction results
        """
        if convert_from_path is None:
            raise ImportError("pdf2image is not installed. Install it with: pip install pdf2image")

        if pytesseract is None:
            raise ImportError("pytesseract is not installed. Install it with: pip install pytesseract")

        try:
            # Convert PDF to images
            logger.info("Converting PDF to images...")
            images = convert_from_path(str(pdf_path), dpi=300)
            logger.info(f"Converted PDF to {len(images)} images")

            # Extract text from each image using OCR
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1}/{len(images)} with OCR...")
                try:
                    # Use Thai language for OCR
                    # If tesseract doesn't have Thai language data, it will fall back to English
                    page_text = pytesseract.image_to_string(
                        image,
                        lang='tha+eng',  # Thai + English
                        config='--psm 6'  # Assume uniform block of text
                    )
                    if page_text.strip():
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"OCR failed for page {i + 1}: {e}")
                    # Try with just English if Thai fails
                    try:
                        page_text = pytesseract.image_to_string(
                            image,
                            lang='eng',
                            config='--psm 6'
                        )
                        if page_text.strip():
                            text_parts.append(page_text)
                    except Exception as e2:
                        logger.error(f"OCR failed even with English for page {i + 1}: {e2}")

            full_text = "\n\n".join(text_parts)

            if not full_text.strip():
                raise Exception("OCR did not extract any text")

            return {
                "text": full_text,
                "method": "ocr",
                "pages": len(images),
                "success": True
            }

        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            raise

    def extract_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Extract images from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of PIL Image objects
        """
        if convert_from_path is None:
            raise ImportError("pdf2image is not installed")

        try:
            images = convert_from_path(pdf_path, dpi=300)
            return images
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            raise
