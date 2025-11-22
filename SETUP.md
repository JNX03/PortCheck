# Setup Guide - Thai Portfolio Analyzer

Complete guide for setting up and running the Thai Portfolio Analyzer.

## Quick Start 🚀

### Option 1: Automated Script (Recommended)

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

The script will:
1. Create `.env` file if it doesn't exist
2. Create virtual environment
3. Install dependencies
4. Start the server

### Option 2: Docker (Easiest)

```bash
# Create .env file with your API key
cp .env.example .env
# Edit .env and add your TYPHOON_API_KEY

# Start with Docker Compose
docker-compose up
```

Access at: http://localhost:8000

### Option 3: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and add your TYPHOON_API_KEY

# 4. Run the application
python main.py
```

## Detailed Installation

### Step 1: System Requirements

**Minimum Requirements:**
- Python 3.8 or higher
- 2GB RAM
- 500MB disk space

**Recommended:**
- Python 3.11+
- 4GB RAM
- 1GB disk space

### Step 2: Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tha \
    tesseract-ocr-eng \
    poppler-utils \
    python3-venv \
    python3-pip
```

#### macOS
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install tesseract tesseract-lang poppler python@3.11
```

#### Windows
1. **Install Python 3.11+** from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation

2. **Install Tesseract OCR:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - Add to PATH: `C:\Program Files\Tesseract-OCR`

3. **Install Poppler:**
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract to: `C:\Program Files\poppler`
   - Add to PATH: `C:\Program Files\poppler\Library\bin`

**Verify installations:**
```bash
tesseract --version
python --version
```

### Step 3: Get Typhoon API Key

1. Visit [OpenTyphoon](https://opentyphoon.ai)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you'll need it in the next step)

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Required configuration in `.env`:**
```bash
TYPHOON_API_KEY=your_actual_api_key_here
TYPHOON_API_URL=https://api.opentyphoon.ai/v1
TYPHOON_MODEL=typhoon-v2.5-30b-a3b-instruct
```

**Optional configuration:**
```bash
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
HOST=0.0.0.0
PORT=8000
```

### Step 5: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Verify Installation

```bash
# Run basic tests
python test_basic.py
```

Expected output:
```
🎉 All tests passed!
Total: 5/5 tests passed
```

### Step 7: Start the Application

```bash
# Start the server
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 8: Access the Application

Open your web browser and navigate to:
```
http://localhost:8000
```

You should see the Thai Portfolio Analyzer interface.

## Docker Setup (Alternative)

### Prerequisites
- Docker installed
- Docker Compose installed

### Steps

1. **Clone and navigate to project:**
```bash
cd PortCheck
```

2. **Create .env file:**
```bash
cp .env.example .env
# Edit .env and add your TYPHOON_API_KEY
```

3. **Build and run:**
```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

4. **Stop the container:**
```bash
docker-compose down
```

### Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Rebuild
docker-compose build --no-cache
```

## Troubleshooting

### Issue: "No module named 'pydantic'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "tesseract is not recognized"
**Solution:**
- Ensure Tesseract is installed
- Add Tesseract to PATH
- Restart terminal

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-tha
```

**Windows:** Add to PATH: `C:\Program Files\Tesseract-OCR`

### Issue: "pdf2image.exceptions.PDFInfoNotInstalledError"
**Solution:** Install Poppler

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:** Add to PATH: `C:\Program Files\poppler\Library\bin`

### Issue: "TYPHOON_API_KEY is required"
**Solution:**
1. Ensure `.env` file exists
2. Add your API key to `.env`:
```bash
TYPHOON_API_KEY=your_actual_key_here
```

### Issue: OCR not working for Thai text
**Solution:** Install Thai language data
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-tha

# macOS (included in tesseract-lang)
brew install tesseract-lang
```

Verify Thai support:
```bash
tesseract --list-langs
# Should show "tha" in the list
```

### Issue: Port 8000 already in use
**Solution:** Change port in `.env`:
```bash
PORT=8080
```

Then access at: http://localhost:8080

### Issue: Large PDF files timing out
**Solution:** Increase timeout in `main.py` or split PDF into smaller files

## Testing the Application

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "typhoon_configured": true,
  "upload_dir": "/path/to/uploads"
}
```

### 2. Test PDF Upload
1. Prepare a Thai PDF document
2. Open http://localhost:8000
3. Upload the PDF
4. Select target field
5. Click "วิเคราะห์ Portfolio"

### 3. API Test with curl
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@your_portfolio.pdf" \
  -F "target_field=engineer"
```

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install Gunicorn:**
```bash
pip install gunicorn
```

2. **Create `gunicorn_config.py`:**
```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5
```

3. **Run with Gunicorn:**
```bash
gunicorn main:app -c gunicorn_config.py
```

### Using Nginx (Reverse Proxy)

**Install Nginx:**
```bash
sudo apt-get install nginx
```

**Configure Nginx (`/etc/nginx/sites-available/portfolio-analyzer`):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/portfolio-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Using Systemd (Auto-start)

**Create service file (`/etc/systemd/system/portfolio-analyzer.service`):**
```ini
[Unit]
Description=Thai Portfolio Analyzer
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/PortCheck
Environment="PATH=/path/to/PortCheck/venv/bin"
ExecStart=/path/to/PortCheck/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable portfolio-analyzer
sudo systemctl start portfolio-analyzer
sudo systemctl status portfolio-analyzer
```

## Performance Optimization

### 1. Use Redis for Caching
Install Redis and cache analysis results for frequently uploaded documents.

### 2. Optimize OCR
- Reduce DPI from 300 to 200 for faster processing
- Process only first few pages for large documents

### 3. Use Celery for Background Tasks
Handle PDF processing asynchronously for better user experience.

### 4. Database Storage
Store analysis results in PostgreSQL/MongoDB for history tracking.

## Security Considerations

1. **API Key Protection:**
   - Never commit `.env` to git
   - Use environment variables in production
   - Rotate keys regularly

2. **File Upload Security:**
   - Validate file types
   - Limit file sizes
   - Scan for malware
   - Auto-delete after processing

3. **Rate Limiting:**
   - Implement rate limiting for API endpoints
   - Use Redis for distributed rate limiting

4. **HTTPS:**
   - Use SSL/TLS in production
   - Get free certificate from Let's Encrypt

## Monitoring and Logging

### Setup Logging
Create `logging_config.py`:
```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"],
    },
}
```

## Getting Help

- **Issues:** Report on GitHub Issues
- **Documentation:** See README.md
- **API Docs:** http://localhost:8000/docs (when running)

## Next Steps

After successful setup:
1. Test with sample PDF documents
2. Customize field mappings in `services/typhoon_analyzer.py`
3. Adjust formality thresholds as needed
4. Add custom styling to the web interface
5. Set up monitoring and logging

---

**Happy Analyzing! 🎉**
