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
    target_field: str = Form(..., description="Target field/position (e.g., doctor, engineer, AI)"),
    judgment_criteria: str = Form("", description="Custom selection criteria (เกณฑ์การเลือก) - optional")
):
    """
    Analyze a Thai portfolio PDF

    - Extracts text from PDF (with OCR fallback)
    - Analyzes formal vs informal language
    - Checks field matching
    - Evaluates certificates and achievements
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
            target_field=target_field,
            judgment_criteria=judgment_criteria
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
            # Medical & Health
            {"value": "doctor", "label": "แพทย์ (Doctor)", "thai": "แพทย์", "category": "medical"},
            {"value": "nurse", "label": "พยาบาล (Nurse)", "thai": "พยาบาล", "category": "medical"},
            {"value": "dentist", "label": "ทันตแพทย์ (Dentist)", "thai": "ทันตแพทย์", "category": "medical"},
            {"value": "pharmacist", "label": "เภสัชกร (Pharmacist)", "thai": "เภสัชกร", "category": "medical"},
            {"value": "medical_tech", "label": "นักเทคนิคการแพทย์ (Medical Technologist)", "thai": "นักเทคนิคการแพทย์", "category": "medical"},
            {"value": "physical_therapist", "label": "นักกายภาพบำบัด (Physical Therapist)", "thai": "นักกายภาพบำบัด", "category": "medical"},
            {"value": "veterinarian", "label": "สัตวแพทย์ (Veterinarian)", "thai": "สัตวแพทย์", "category": "medical"},

            # Engineering & Technology
            {"value": "engineer", "label": "วิศวกร (Engineer)", "thai": "วิศวกร", "category": "engineering"},
            {"value": "software_engineer", "label": "วิศวกรซอฟต์แวร์ (Software Engineer)", "thai": "วิศวกรซอฟต์แวร์", "category": "engineering"},
            {"value": "civil_engineer", "label": "วิศวกรโยธา (Civil Engineer)", "thai": "วิศวกรโยธา", "category": "engineering"},
            {"value": "mechanical_engineer", "label": "วิศวกรเครื่องกล (Mechanical Engineer)", "thai": "วิศวกรเครื่องกล", "category": "engineering"},
            {"value": "electrical_engineer", "label": "วิศวกรไฟฟ้า (Electrical Engineer)", "thai": "วิศวกรไฟฟ้า", "category": "engineering"},
            {"value": "chemical_engineer", "label": "วิศวกรเคมี (Chemical Engineer)", "thai": "วิศวกรเคมี", "category": "engineering"},
            {"value": "industrial_engineer", "label": "วิศวกรอุตสาหการ (Industrial Engineer)", "thai": "วิศวกรอุตสาหการ", "category": "engineering"},

            # IT & Computer Science
            {"value": "ai", "label": "AI/Data Science", "thai": "AI/วิทยาการข้อมูล", "category": "it"},
            {"value": "data_scientist", "label": "นักวิทยาศาสตร์ข้อมูล (Data Scientist)", "thai": "นักวิทยาศาสตร์ข้อมูล", "category": "it"},
            {"value": "programmer", "label": "โปรแกรมเมอร์ (Programmer)", "thai": "โปรแกรมเมอร์", "category": "it"},
            {"value": "web_developer", "label": "นักพัฒนาเว็บ (Web Developer)", "thai": "นักพัฒนาเว็บ", "category": "it"},
            {"value": "mobile_developer", "label": "นักพัฒนาแอปพลิเคชัน (Mobile Developer)", "thai": "นักพัฒนาแอปพลิเคชัน", "category": "it"},
            {"value": "devops", "label": "DevOps Engineer", "thai": "วิศวกร DevOps", "category": "it"},
            {"value": "cybersecurity", "label": "ผู้เชี่ยวชาญความปลอดภัย (Cybersecurity)", "thai": "ผู้เชี่ยวชาญความปลอดภัย", "category": "it"},
            {"value": "network_engineer", "label": "วิศวกรเครือข่าย (Network Engineer)", "thai": "วิศวกรเครือข่าย", "category": "it"},

            # Business & Finance
            {"value": "business", "label": "ธุรกิจ (Business)", "thai": "ธุรกิจ", "category": "business"},
            {"value": "accountant", "label": "นักบัญชี (Accountant)", "thai": "นักบัญชี", "category": "business"},
            {"value": "auditor", "label": "ผู้สอบบัญชี (Auditor)", "thai": "ผู้สอบบัญชี", "category": "business"},
            {"value": "financial_analyst", "label": "นักวิเคราะห์การเงิน (Financial Analyst)", "thai": "นักวิเคราะห์การเงิน", "category": "business"},
            {"value": "marketing", "label": "นักการตลาด (Marketing)", "thai": "นักการตลาด", "category": "business"},
            {"value": "hr", "label": "ทรัพยากรบุคคล (HR)", "thai": "ทรัพยากรบุคคล", "category": "business"},
            {"value": "entrepreneur", "label": "ผู้ประกอบการ (Entrepreneur)", "thai": "ผู้ประกอบการ", "category": "business"},
            {"value": "investment_banker", "label": "นักลงทุน (Investment Banker)", "thai": "นักลงทุน", "category": "business"},

            # Education
            {"value": "teacher", "label": "ครู (Teacher)", "thai": "ครู", "category": "education"},
            {"value": "professor", "label": "อาจารย์ (Professor)", "thai": "อาจารย์", "category": "education"},
            {"value": "researcher", "label": "นักวิจัย (Researcher)", "thai": "นักวิจัย", "category": "education"},
            {"value": "tutor", "label": "ติวเตอร์ (Tutor)", "thai": "ติวเตอร์", "category": "education"},

            # Creative & Design
            {"value": "designer", "label": "นักออกแบบ (Designer)", "thai": "นักออกแบบ", "category": "creative"},
            {"value": "graphic_designer", "label": "นักออกแบบกราฟิก (Graphic Designer)", "thai": "นักออกแบบกราฟิก", "category": "creative"},
            {"value": "ux_ui_designer", "label": "UX/UI Designer", "thai": "นักออกแบบ UX/UI", "category": "creative"},
            {"value": "architect", "label": "สถาปนิก (Architect)", "thai": "สถาปนิก", "category": "creative"},
            {"value": "interior_designer", "label": "นักออกแบบตกแต่งภายใน (Interior Designer)", "thai": "นักออกแบบตกแต่งภายใน", "category": "creative"},
            {"value": "animator", "label": "นักแอนิเมชั่น (Animator)", "thai": "นักแอนิเมชั่น", "category": "creative"},
            {"value": "video_editor", "label": "นักตัดต่อวิดีโอ (Video Editor)", "thai": "นักตัดต่อวิดีโอ", "category": "creative"},
            {"value": "photographer", "label": "ช่างภาพ (Photographer)", "thai": "ช่างภาพ", "category": "creative"},

            # Legal & Government
            {"value": "lawyer", "label": "ทนายความ (Lawyer)", "thai": "ทนายความ", "category": "legal"},
            {"value": "judge", "label": "ผู้พิพากษา (Judge)", "thai": "ผู้พิพากษา", "category": "legal"},
            {"value": "government_officer", "label": "ข้าราชการ (Government Officer)", "thai": "ข้าราชการ", "category": "legal"},
            {"value": "diplomat", "label": "นักการทูต (Diplomat)", "thai": "นักการทูต", "category": "legal"},

            # Science
            {"value": "scientist", "label": "นักวิทยาศาสตร์ (Scientist)", "thai": "นักวิทยาศาสตร์", "category": "science"},
            {"value": "biologist", "label": "นักชีววิทยา (Biologist)", "thai": "นักชีววิทยา", "category": "science"},
            {"value": "chemist", "label": "นักเคมี (Chemist)", "thai": "นักเคมี", "category": "science"},
            {"value": "physicist", "label": "นักฟิสิกส์ (Physicist)", "thai": "นักฟิสิกส์", "category": "science"},

            # Media & Communication
            {"value": "journalist", "label": "นักข่าว (Journalist)", "thai": "นักข่าว", "category": "media"},
            {"value": "content_creator", "label": "ครีเอเตอร์ (Content Creator)", "thai": "ครีเอเตอร์", "category": "media"},
            {"value": "public_relations", "label": "นักประชาสัมพันธ์ (Public Relations)", "thai": "นักประชาสัมพันธ์", "category": "media"},
            {"value": "translator", "label": "นักแปล (Translator)", "thai": "นักแปล", "category": "media"},

            # Hospitality & Tourism
            {"value": "chef", "label": "เชฟ (Chef)", "thai": "เชฟ", "category": "hospitality"},
            {"value": "hotel_manager", "label": "ผู้จัดการโรงแรม (Hotel Manager)", "thai": "ผู้จัดการโรงแรม", "category": "hospitality"},
            {"value": "tour_guide", "label": "ไกด์นำเที่ยว (Tour Guide)", "thai": "ไกด์นำเที่ยว", "category": "hospitality"},

            # Other
            {"value": "pilot", "label": "นักบิน (Pilot)", "thai": "นักบิน", "category": "other"},
            {"value": "athlete", "label": "นักกีฬา (Athlete)", "thai": "นักกีฬา", "category": "other"},
            {"value": "artist", "label": "ศิลปิน (Artist)", "thai": "ศิลปิน", "category": "other"},
            {"value": "musician", "label": "นักดนตรี (Musician)", "thai": "นักดนตรี", "category": "other"},
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
