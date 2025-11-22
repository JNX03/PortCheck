# Usage Guide - Thai Portfolio Analyzer

Complete guide for using the Thai Portfolio Analyzer application.

## Table of Contents
- [Getting Started](#getting-started)
- [Web Interface Guide](#web-interface-guide)
- [API Usage](#api-usage)
- [Understanding Results](#understanding-results)
- [Best Practices](#best-practices)
- [Common Use Cases](#common-use-cases)
- [Tips & Tricks](#tips--tricks)

## Getting Started

### Prerequisites
- Application is running (see SETUP.md)
- Thai PDF portfolio document ready
- Know the target field/position

### Access the Application
1. Open web browser
2. Navigate to: http://localhost:8000
3. You should see the Thai Portfolio Analyzer interface

## Web Interface Guide

### Step 1: Upload PDF

**Option A: Click to Upload**
1. Click on the upload area (large box with folder icon)
2. Select your PDF file from file dialog
3. File name will appear below the upload area

**Option B: Drag and Drop**
1. Drag your PDF file from file explorer
2. Drop it onto the upload area
3. File name will appear below the upload area

**Supported Formats:**
- PDF files only (`.pdf`)
- Maximum size: 10MB (configurable)
- Text-based or image-based PDFs both supported

### Step 2: Select Target Field

Choose the field/position from the dropdown menu:

- **แพทย์ (Doctor)**: Medical profession
- **วิศวกร (Engineer)**: Engineering fields
- **AI/Data Science**: AI, ML, Data Science
- **ธุรกิจ (Business)**: Business, management
- **ครู (Teacher)**: Education, teaching
- **พยาบาล (Nurse)**: Nursing
- **สถาปนิก (Architect)**: Architecture
- **นักออกแบบ (Designer)**: Design fields
- **ทนายความ (Lawyer)**: Law
- **นักบัญชี (Accountant)**: Accounting, finance

### Step 3: Analyze

1. Click **"วิเคราะห์ Portfolio"** button
2. Wait for processing (usually 10-30 seconds)
3. Processing indicator will show:
   - Spinning animation
   - "กำลังวิเคราะห์..." message

**Processing Time:**
- Small PDFs (1-5 pages): 10-15 seconds
- Medium PDFs (5-10 pages): 15-30 seconds
- Large PDFs (10+ pages): 30-60 seconds
- Image-based PDFs: Add 10-20 seconds for OCR

### Step 4: Review Results

Results are displayed in sections:

#### 1. Summary Box (Top)
**Overall Analysis:**
- ✅ or ⚠️ indicators
- Quick summary of findings
- Field match status

**Statistics:**
- **คะแนนความเป็นทางการ**: Formality score (0-100%)
- **ระดับภาษา**: Formality level
- **จุดที่ควรปรับปรุง**: Number of issues found
- **จำนวนตัวอักษร**: Text length

#### 2. Field Matching Section
**Shows:**
- ✅ Match or ❌ No match status
- Confidence percentage
- Detected fields in portfolio
- Evidence supporting the decision
- Recommendations for improvement

#### 3. Key Findings
**Highlights:**
- Overall formality assessment
- Expertise areas detected
- Number of issues found

#### 4. Language Issues
**For each issue found:**
- **Highlighted text**: The informal word/phrase
- **Severity badge**: High / Medium / Low
- **Suggestion**: Formal alternative
- **Explanation**: Why it's an issue
- **Context**: Surrounding text

**Severity Levels:**
- 🔴 **สูง (High)**: Very informal, should definitely change
- 🟡 **ปานกลาง (Medium)**: Moderately informal, recommended to change
- 🔵 **ต่ำ (Low)**: Slightly informal, optional to change

## API Usage

### Using curl

**Basic request:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@portfolio.pdf" \
  -F "target_field=engineer"
```

**With custom API endpoint:**
```bash
curl -X POST http://your-domain.com:8000/api/analyze \
  -F "file=@portfolio.pdf" \
  -F "target_field=doctor" \
  -o results.json
```

### Using Python

```python
import requests

url = "http://localhost:8000/api/analyze"

files = {
    'file': open('portfolio.pdf', 'rb')
}

data = {
    'target_field': 'engineer'
}

response = requests.post(url, files=files, data=data)
results = response.json()

print(f"Formality Score: {results['overall_formality_score']}")
print(f"Issues Found: {len(results['language_issues'])}")
```

### Using JavaScript

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('target_field', 'ai');

fetch('http://localhost:8000/api/analyze', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Analysis Results:', data);
})
.catch(error => {
    console.error('Error:', error);
});
```

### Response Format

```json
{
  "success": true,
  "text_length": 1500,
  "extraction_method": "direct",
  "pages_processed": 3,
  "overall_formality_score": 0.75,
  "formality_level": "formal",
  "language_issues": [
    {
      "text": "เจ๋งมาก",
      "start_pos": 250,
      "end_pos": 257,
      "issue_type": "informal_word",
      "severity": "high",
      "suggestion": "ยอดเยี่ยม",
      "explanation": "คำว่า 'เจ๋ง' เป็นภาษาพูดที่ไม่เป็นทางการ",
      "context": "ผลงานนี้เจ๋งมากและได้รับรางวัล"
    }
  ],
  "field_match": {
    "target_field": "engineer",
    "matches": true,
    "confidence": 0.85,
    "detected_fields": ["วิศวกรรม", "เทคโนโลยี"],
    "evidence": ["มีประสบการณ์ด้านการพัฒนาซอฟต์แวร์"],
    "recommendations": ["เพิ่มรายละเอียดโครงการเฉพาะทาง"]
  },
  "summary": "Portfolio ใช้ภาษาเป็นทางการและตรงกับสาขาวิศวกร",
  "key_findings": [
    "ภาษาที่ใช้มีความเป็นทางการในระดับพอใช้",
    "ตรวจพบความเชี่ยวชาญใน: วิศวกรรม, เทคโนโลยี",
    "พบจุดที่ควรปรับปรุง 1 จุด"
  ]
}
```

## Understanding Results

### Formality Score Interpretation

| Score | Level | Meaning |
|-------|-------|---------|
| 90-100% | Highly Formal | Excellent formal language usage |
| 75-89% | Formal | Good formal language, minor issues |
| 60-74% | Mixed | Mix of formal and informal language |
| 40-59% | Informal | Significant informal language |
| 0-39% | Highly Informal | Mostly informal/spoken language |

### Formality Levels

**highly_formal (เป็นทางการมาก)**
- All text uses proper formal Thai
- Suitable for official documents
- No improvements needed

**formal (เป็นทางการ)**
- Mostly formal language
- Few minor issues
- Minor improvements suggested

**mixed (ผสม)**
- Mix of formal and informal
- Several issues to address
- Moderate improvements needed

**informal (ไม่เป็นทางการ)**
- Significant informal language
- Many issues found
- Substantial improvements required

**highly_informal (ไม่เป็นทางการมาก)**
- Mostly spoken language
- Major rewrite recommended
- Not suitable for formal portfolios

### Common Informal Patterns Detected

**Informal Words:**
- เจ๋ง → ยอดเยี่ยม, โดดเด่น
- เท่ห์ → น่าประทับใจ, สง่างาม
- เก่ง → มีความสามารถ, เชี่ยวชาญ
- สุดยอด → เป็นเลิศ, ดีเด่น
- ชอบมาก → มีความสนใจอย่างยิ่ง

**Spoken Endings:**
- ครับผม → ครับ (or remove)
- จ้า, จ๊ะ → (remove)
- นะ, เนอะ → (remove)
- เหรอ → หรือไม่

**Casual Expressions:**
- อะไรก็แล้วแต่ → ยืดหยุ่นตามความเหมาะสม
- ไม่รู้ซิ → ยังไม่แน่ใจ
- ก็ได้ → เป็นไปได้

## Best Practices

### For Best Results

1. **PDF Quality:**
   - Use high-quality PDFs
   - Ensure text is searchable (not scanned images if possible)
   - Clear font and proper spacing

2. **Content:**
   - Use complete sentences
   - Proper grammar and spelling
   - Organized sections

3. **Language:**
   - Use formal Thai (ภาษาเขียน)
   - Avoid spoken language (ภาษาพูด)
   - Use professional terminology

4. **Field Matching:**
   - Include relevant keywords
   - Mention specific skills and experiences
   - Align content with target field

### Creating a Good Portfolio

**Do's:**
- ✅ Use formal language throughout
- ✅ Include relevant experiences
- ✅ Quantify achievements
- ✅ Use professional terms
- ✅ Proper formatting

**Don'ts:**
- ❌ Use casual/spoken language
- ❌ Include irrelevant information
- ❌ Use overly complex sentences
- ❌ Forget to proofread
- ❌ Mix multiple fonts unnecessarily

## Common Use Cases

### Use Case 1: University Application
**Scenario:** Applying to medical school

**Steps:**
1. Upload portfolio PDF
2. Select "แพทย์ (Doctor)"
3. Review language issues
4. Check field matching
5. Revise portfolio based on suggestions
6. Re-upload and verify improvements

### Use Case 2: Job Application
**Scenario:** Applying for software engineer position

**Steps:**
1. Upload CV/Portfolio
2. Select "วิศวกร (Engineer)" or "AI/Data Science"
3. Verify technical terms are formal
4. Ensure experience matches field
5. Implement recommendations

### Use Case 3: Scholarship Application
**Scenario:** Applying for academic scholarship

**Steps:**
1. Upload statement of purpose
2. Select relevant field
3. Ensure highly formal language (aim for 90%+)
4. Verify no spoken language patterns
5. Polish until no issues found

### Use Case 4: Batch Processing
**Scenario:** HR reviewing multiple portfolios

**API Approach:**
```python
import os
import requests
import json

portfolio_dir = "portfolios/"
target_field = "engineer"

results = []
for filename in os.listdir(portfolio_dir):
    if filename.endswith('.pdf'):
        filepath = os.path.join(portfolio_dir, filename)

        with open(filepath, 'rb') as f:
            response = requests.post(
                'http://localhost:8000/api/analyze',
                files={'file': f},
                data={'target_field': target_field}
            )

        result = response.json()
        results.append({
            'filename': filename,
            'formality_score': result['overall_formality_score'],
            'matches': result['field_match']['matches'],
            'issues_count': len(result['language_issues'])
        })

# Save results
with open('batch_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

## Tips & Tricks

### Performance Tips

1. **Faster Processing:**
   - Use text-based PDFs (not scanned images)
   - Smaller file sizes process faster
   - OCR adds 10-20 seconds

2. **Better Results:**
   - High-quality PDFs get better text extraction
   - Clear fonts improve OCR accuracy
   - Proper Thai encoding prevents issues

### Improving Your Portfolio

1. **After First Analysis:**
   - Address all "high" severity issues first
   - Then fix "medium" severity issues
   - Consider "low" severity suggestions

2. **Iterative Improvement:**
   - Fix issues → re-upload → verify
   - Aim for 85%+ formality score
   - Ensure field matching is confident

3. **Common Fixes:**
   - Replace informal words with suggestions
   - Remove casual sentence endings
   - Use professional terminology
   - Verify grammar and spelling

### Understanding Field Matching

**High Confidence (80-100%):**
- Portfolio strongly matches field
- Clear evidence of relevant experience
- Appropriate keywords present

**Medium Confidence (60-79%):**
- Some match with target field
- May need more specific content
- Consider adding relevant details

**Low Confidence (<60%):**
- Weak match or mismatch
- May be applying to wrong field
- Significant revision recommended

### Troubleshooting

**Issue: "Could not extract text"**
- PDF may be encrypted
- Try re-saving PDF
- Check if file is corrupted

**Issue: "OCR not detecting Thai text"**
- Ensure Tesseract has Thai language data
- Check image quality in PDF
- Try adjusting PDF DPI

**Issue: "Too many false positives"**
- Some formal words may be flagged
- Use context to judge suggestion validity
- AI model is trained but not perfect

**Issue: "Field not matching despite relevant content"**
- Add more specific keywords
- Mention relevant projects/skills
- Use standard field terminology

## Advanced Usage

### Custom Field Definitions

To add custom fields, edit `services/typhoon_analyzer.py`:

```python
field_mapping = {
    "custom_field": "keywords, related, to, field",
    # Add your custom field here
}
```

### Adjusting Formality Threshold

Edit `services/pdf_processor.py`:

```python
self.min_text_threshold = 50  # Lower for shorter documents
```

### Batch Processing Script

Save as `batch_analyze.py`:

```python
#!/usr/bin/env python3
import sys
import requests

def analyze_portfolio(pdf_path, target_field):
    with open(pdf_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/api/analyze',
            files={'file': f},
            data={'target_field': target_field}
        )
    return response.json()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python batch_analyze.py <pdf_file> <target_field>")
        sys.exit(1)

    result = analyze_portfolio(sys.argv[1], sys.argv[2])

    print(f"\nFormality Score: {result['overall_formality_score']:.1%}")
    print(f"Issues Found: {len(result['language_issues'])}")
    print(f"Field Match: {'✅' if result['field_match']['matches'] else '❌'}")
    print(f"\nSummary: {result['summary']}")
```

## Getting Help

### Resources
- **Setup Issues**: See SETUP.md
- **API Documentation**: http://localhost:8000/docs
- **Project Documentation**: See README.md

### Common Questions

**Q: How accurate is the language analysis?**
A: The Typhoon AI model is trained on Thai language and provides ~85-90% accuracy. Always review suggestions in context.

**Q: Can it handle scanned PDFs?**
A: Yes! OCR (Tesseract) automatically processes image-based PDFs.

**Q: What PDF size is supported?**
A: Default limit is 10MB. Configurable in `.env` file.

**Q: How long are files stored?**
A: Files are automatically deleted after processing for privacy.

**Q: Can I use this offline?**
A: No, it requires internet connection for Typhoon AI API.

**Q: Is my data secure?**
A: Files are processed locally and deleted immediately. Only text is sent to Typhoon AI API for analysis.

---

**Happy Analyzing! 📄✨**

For technical support or feature requests, please open an issue on GitHub.
