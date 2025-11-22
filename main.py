"""
Thai Portfolio Analyzer - FastAPI Application
Analyzes Thai portfolios for formal language usage and field matching
"""

import os
import logging
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from services.pdf_processor import PDFProcessor
from services.typhoon_analyzer import TyphoonAnalyzer
from models.schemas import AnalysisResult, LanguageIssue, FieldMatch

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Thai Portfolio Analyzer",
    description="Analyze Thai portfolios for formal language and field matching",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize services
pdf_processor = PDFProcessor()
typhoon_analyzer = TyphoonAnalyzer(
    api_key=os.getenv("TYPHOON_API_KEY"),
    api_url=os.getenv("TYPHOON_API_URL", "https://api.opentyphoon.ai/v1"),
    model=os.getenv("TYPHOON_MODEL", "typhoon-v2.5-30b-a3b-instruct")
)

# Mount static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML page"""
    html_file = Path("templates/index.html")
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Thai Portfolio Analyzer</title></head>
    <body>
        <h1>Thai Portfolio Analyzer</h1>
        <p>Web interface is being set up. Please check templates/index.html</p>
    </body>
    </html>
    """


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_portfolio(
    file: UploadFile = File(..., description="PDF file to analyze"),
    target_field: str = Form(..., description="Target field/position (e.g., doctor, engineer, AI)")
):
    """
    Analyze a Thai portfolio PDF

    - Extracts text from PDF (with OCR fallback)
    - Analyzes formal vs informal language
    - Checks field matching
    - Returns highlighted issues with suggestions
    """
    try:
        # Validate file
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        logger.info(f"Processing file: {file.filename} for field: {target_field}")

        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Step 1: Extract text from PDF
        logger.info("Extracting text from PDF...")
        extraction_result = pdf_processor.extract_text(str(file_path))

        if not extraction_result["text"].strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. Please ensure the file is readable."
            )

        logger.info(f"Extracted {len(extraction_result['text'])} characters using method: {extraction_result['method']}")

        # Step 2: Analyze language and content with Typhoon AI
        logger.info("Analyzing content with Typhoon AI...")
        analysis = await typhoon_analyzer.analyze_portfolio(
            text=extraction_result["text"],
            target_field=target_field
        )

        # Add extraction metadata
        analysis.extraction_method = extraction_result["method"]
        analysis.pages_processed = extraction_result.get("pages", 0)

        logger.info(f"Analysis complete. Found {len(analysis.language_issues)} language issues")

        # Clean up uploaded file
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file: {e}")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "typhoon_configured": bool(os.getenv("TYPHOON_API_KEY")),
        "upload_dir": str(UPLOAD_DIR.absolute())
    }


@app.get("/api/fields")
async def get_supported_fields():
    """Get list of supported fields/positions"""
    return {
        "fields": [
            {"value": "doctor", "label": "แพทย์ (Doctor)", "thai": "แพทย์"},
            {"value": "engineer", "label": "วิศวกร (Engineer)", "thai": "วิศวกร"},
            {"value": "ai", "label": "AI/Data Science", "thai": "AI/วิทยาการข้อมูล"},
            {"value": "business", "label": "ธุรกิจ (Business)", "thai": "ธุรกิจ"},
            {"value": "teacher", "label": "ครู (Teacher)", "thai": "ครู"},
            {"value": "nurse", "label": "พยาบาล (Nurse)", "thai": "พยาบาล"},
            {"value": "architect", "label": "สถาปนิก (Architect)", "thai": "สถาปนิก"},
            {"value": "designer", "label": "นักออกแบบ (Designer)", "thai": "นักออกแบบ"},
            {"value": "lawyer", "label": "ทนายความ (Lawyer)", "thai": "ทนายความ"},
            {"value": "accountant", "label": "นักบัญชี (Accountant)", "thai": "นักบัญชี"},
        ]
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    logger.info(f"Starting Thai Portfolio Analyzer on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
