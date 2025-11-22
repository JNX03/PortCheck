# Thai Portfolio Analyzer 📄

A comprehensive web application for analyzing Thai portfolios using FastAPI and Typhoon AI. This tool checks for formal vs. informal language usage (ภาษาเขียน vs ภาษาพูด) and validates whether the portfolio matches the target field/position.

## Features ✨

- **PDF Upload & Processing**: Upload PDF portfolios with automatic text extraction
- **OCR Fallback**: Automatically uses OCR for image-based PDFs (with Tesseract)
- **Thai Language Analysis**: Detects informal/spoken language (ภาษาพูด) in formal documents
- **Formal Language Suggestions**: Provides recommendations for more formal alternatives
- **Field Matching**: Checks if portfolio content matches the target position (doctor, engineer, AI, etc.)
- **Interactive Web Interface**: Beautiful, responsive UI with hover tooltips
- **Typhoon AI Integration**: Uses `typhoon-v2.5-30b-a3b-instruct` model for advanced Thai language understanding

## Tech Stack 🛠️

- **Backend**: FastAPI, Python 3.8+
- **AI Model**: Typhoon AI (typhoon-v2.5-30b-a3b-instruct)
- **PDF Processing**: PyPDF2, pdf2image, pytesseract
- **OCR**: Tesseract OCR with Thai language support
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## Installation 🚀

### Prerequisites

1. **Python 3.8 or higher**
2. **Tesseract OCR** (for image-based PDF processing)
3. **Poppler** (for PDF to image conversion)
4. **Typhoon API Key** (get from [OpenTyphoon](https://opentyphoon.ai))

### Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-tha poppler-utils
```

#### On macOS:
```bash
brew install tesseract tesseract-lang poppler
```

#### On Windows:
1. Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. Download and install [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/)
3. Add both to your PATH

### Install Python Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd PortCheck

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Typhoon API key:
```bash
TYPHOON_API_KEY=your_api_key_here
TYPHOON_API_URL=https://api.opentyphoon.ai/v1
TYPHOON_MODEL=typhoon-v2.5-30b-a3b-instruct
```

## Usage 💻

### Start the Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: `http://localhost:8000`

### Using the Web Interface

1. **Open your browser** and navigate to `http://localhost:8000`
2. **Upload a PDF**: Click or drag-and-drop your portfolio PDF
3. **Select target field**: Choose the position you're applying for
4. **Click "วิเคราะห์ Portfolio"**: Wait for the analysis to complete
5. **Review results**: See language issues, suggestions, and field matching analysis

### API Endpoints

#### POST `/api/analyze`
Analyze a portfolio PDF.

**Request:**
- `file`: PDF file (multipart/form-data)
- `target_field`: Target field/position (form field)

**Response:**
```json
{
  "success": true,
  "text_length": 1500,
  "extraction_method": "direct",
  "overall_formality_score": 0.75,
  "formality_level": "formal",
  "language_issues": [
    {
      "text": "เจ๋ง",
      "start_pos": 150,
      "end_pos": 154,
      "issue_type": "informal_word",
      "severity": "high",
      "suggestion": "ยอดเยี่ยม",
      "explanation": "คำว่า 'เจ๋ง' เป็นภาษาพูดที่ไม่เป็นทางการ",
      "context": "ผลงานนี้เจ๋งมาก"
    }
  ],
  "field_match": {
    "target_field": "doctor",
    "matches": true,
    "confidence": 0.85,
    "detected_fields": ["แพทย์", "สาธารณสุข"],
    "evidence": ["พบการกล่าวถึงประสบการณ์ทางการแพทย์"],
    "recommendations": ["เน้นทักษะเฉพาะทางให้ชัดเจนขึ้น"]
  },
  "summary": "Portfolio ใช้ภาษาเป็นทางการ และตรงกับสาขาแพทย์",
  "key_findings": ["พบการใช้ภาษาพูด 1 จุด", "ความเชี่ยวชาญตรงกับสาขา"]
}
```

#### GET `/api/health`
Health check endpoint.

#### GET `/api/fields`
Get list of supported fields/positions.

## Project Structure 📁

```
PortCheck/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py   # PDF text extraction & OCR
│   └── typhoon_analyzer.py # Typhoon AI integration
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/              # (optional) Additional CSS
│   └── js/               # (optional) Additional JS
└── uploads/              # Temporary upload directory (auto-created)
```

## How It Works 🔍

### 1. PDF Processing
- First attempts direct text extraction using PyPDF2
- If extraction yields < 100 characters, falls back to OCR
- OCR uses Tesseract with Thai language support (tha+eng)
- Converts PDF pages to images at 300 DPI for optimal quality

### 2. Language Analysis
The Typhoon AI model analyzes the text to:
- Identify informal/spoken language patterns
- Calculate overall formality score (0-1)
- Provide specific suggestions for formal alternatives
- Explain why each issue is problematic

Common informal patterns detected:
- Informal words: เจ๋ง, เท่ห์, เก่ง, สุดยอด
- Spoken endings: ครับผม, จ้า, นะ, เนอะ
- Casual expressions: อะไรก็แล้วแต่, ไม่รู้ซิ

### 3. Field Matching
Analyzes portfolio content against target field:
- Detects skills, experiences, and keywords
- Compares with expected field requirements
- Provides confidence score and evidence
- Suggests improvements for better alignment

### 4. Results Display
- Interactive web interface with highlighting
- Hover tooltips for suggestions
- Color-coded severity levels (high/medium/low)
- Comprehensive summary and statistics

## Supported Fields 🎯

- แพทย์ (Doctor)
- วิศวกร (Engineer)
- AI/Data Science
- ธุรกิจ (Business)
- ครู (Teacher)
- พยาบาล (Nurse)
- สถาปนิก (Architect)
- นักออกแบบ (Designer)
- ทนายความ (Lawyer)
- นักบัญชี (Accountant)

## Troubleshooting 🔧

### OCR Not Working
- Ensure Tesseract is installed: `tesseract --version`
- Install Thai language data: `sudo apt-get install tesseract-ocr-tha`
- Check Tesseract path in system PATH

### PDF Conversion Issues
- Install Poppler: Required for pdf2image
- Ubuntu/Debian: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`

### Typhoon API Errors
- Verify API key is correct in `.env`
- Check API endpoint URL
- Ensure you have API credits

### Empty Text Extraction
- PDF may be encrypted or corrupted
- Try re-saving the PDF
- Check if PDF contains actual text (not just images)

## Performance Tips 💡

1. **Large PDFs**: May take longer to process (especially with OCR)
2. **API Limits**: Typhoon AI has rate limits - consider caching results
3. **Memory**: OCR can be memory-intensive for large documents
4. **Thai Language**: Ensure proper UTF-8 encoding throughout

## Development 👨‍💻

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black .

# Lint
flake8 .
```

## Contributing 🤝

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License 📝

This project is licensed under the MIT License.

## Acknowledgments 🙏

- [Typhoon AI](https://opentyphoon.ai) for the Thai language model
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for OCR capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework

## Contact 📧

For questions or support, please open an issue on GitHub.

---

Made with ❤️ for Thai language processing
