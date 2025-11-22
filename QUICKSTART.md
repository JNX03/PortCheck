# Thai Portfolio Analyzer - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Get API Key
Visit https://opentyphoon.ai and get your API key

### Step 2: Configure
```bash
cp .env.example .env
# Edit .env and add: TYPHOON_API_KEY=your_key_here
```

### Step 3: Run
```bash
./start.sh           # Linux/macOS
# OR
start.bat            # Windows
# OR
docker-compose up    # Docker
```

Then open: **http://localhost:8000**

## 📋 System Requirements

### Linux/Ubuntu
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-tha poppler-utils
```

### macOS
```bash
brew install tesseract tesseract-lang poppler
```

### Windows
1. Install Python 3.11+ from python.org
2. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
3. Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases/

## 📝 How to Use

1. **Upload PDF**: Drag & drop your Thai portfolio PDF
2. **Select Field**: Choose target position (doctor, engineer, AI, etc.)
3. **Analyze**: Click "วิเคราะห์ Portfolio"
4. **Review**: Check results, suggestions, and field matching

## 🎯 What It Does

✅ Detects informal Thai language (ภาษาพูด)
✅ Suggests formal alternatives (ภาษาเขียน)
✅ Checks if portfolio matches target field
✅ Provides improvement recommendations
✅ Works with both text and image PDFs (OCR)

## 📊 Key Features

- **Formality Score**: 0-100% (aim for 85%+)
- **Issue Detection**: High/Medium/Low severity
- **Field Matching**: 10 supported fields
- **OCR Support**: Automatically processes image PDFs
- **Web Interface**: Beautiful, responsive design
- **API Access**: RESTful API for automation

## 🔧 Troubleshooting

**No text extracted?**
- Ensure PDF is not encrypted
- OCR will automatically activate for image PDFs

**Tesseract not found?**
- Install Tesseract (see System Requirements)
- Add to PATH on Windows

**API key error?**
- Check .env file exists
- Verify TYPHOON_API_KEY is set correctly

## 📚 Documentation

- **README.md** - Full project overview
- **SETUP.md** - Detailed installation guide
- **USAGE.md** - Complete user manual

## 🌐 API Example

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@portfolio.pdf" \
  -F "target_field=engineer"
```

## 💡 Pro Tips

1. Use text-based PDFs for faster processing
2. Fix "high" severity issues first
3. Aim for 85%+ formality score
4. Review AI suggestions in context
5. Re-upload after fixes to verify improvement

---

**Need Help?** See SETUP.md and USAGE.md for detailed guides.

**Ready to Start?** Run `./start.sh` or `start.bat` now!
