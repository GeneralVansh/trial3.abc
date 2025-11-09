# UGC Internship Credit Portal (Full-stack Demo)

A comprehensive web application for automated certificate extraction and internship credit evaluation using AI-powered OCR, NLP, and curriculum matching.

## Features

### Certificate Auto-Extraction
- **Multi-format Support**: Upload images (PNG, JPG), PDFs (searchable/scanned), DOCX, or paste text
- **OCR Processing**: Automatic text extraction using Tesseract OCR
- **Smart Field Detection**: Regex + spaCy NER for extracting:
  - Student name, APAAR ID, Institution code
  - Organization name, Internship title
  - Start/end dates, Total hours
  - Certificate ID, GST, CIN
  - Signatory name and email
- **Confidence Scoring**: Each field gets a confidence score (0.0–1.0)

### Auto-Fill Student Form
- Automatic form population with extracted data
- Visual confidence indicators for each field
- Highlights low-confidence fields (< 75%) for manual verification
- Animated field filling for better UX
- Student can edit/verify any field before submission

### Credit Evaluation Pipeline
1. **CEESCM Tokenization**: Normalize internship descriptions
2. **WMD Matching**: Semantic similarity against curriculum database
3. **Credit Calculation**: Based on hours and equivalency decision
4. **Human-in-the-Loop**: Low-confidence submissions sent to mentor review

### Mentor Dashboard
- Review queue for flagged submissions
- Edit fields and add custom matching keywords
- Re-run curriculum matching
- Approve and push to ABC simulator

### ABC Integration
- Automatic push for high-confidence, equivalent internships
- Deterministic token generation (demo mode)
- Manual push option for mentor-reviewed submissions

### 🎓 ABC/UGC Portal (NEW!)
- **Separate student portal** for checking approval status
- **Student Authentication**: Login with APAAR ID and password
- **Dashboard Features**:
  - View all approved submissions
  - Check awarded credits and approval details
  - Download certificates and reports
  - Track submission history
- **Auto-account Creation**: Student accounts created automatically when mentor approves submissions

## Tech Stack

**Backend:**
- Flask 3.0 (Python web framework)
- pytesseract (OCR)
- pdfplumber & pdf2image (PDF processing)
- python-docx (DOCX reading)
- spaCy 3.7 + en_core_web_sm (NLP/NER)
- reportlab (PDF report generation)
- bcrypt (password hashing for ABC portal)

**Frontend:**
- Bootstrap 5 (responsive UI)
- Vanilla JavaScript (no frameworks)
- Custom CSS animations

**Data Storage:**
- JSON file-based (no database required for demo)
- Organized folder structure for uploads/reports

## Installation

### Prerequisites

#### 1. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
Add Tesseract to PATH during installation.

#### 2. Install Poppler (for PDF to image conversion)

**Ubuntu/Debian:**
```bash
sudo apt install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

**Windows:**
Download from: https://github.com/oschwartz10612/poppler-windows/releases
Extract and add `bin/` folder to PATH.

### Python Setup

1. **Clone or download this project**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download spaCy language model:**
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

Or use:
```bash
python -m spacy download en_core_web_sm
```

## Running the Application

### Start the Flask server:

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

### Demo Credentials

**Mentor Login:**
- Username: `mentor`
- Password: `mentorpass`

**ABC Portal Student Login (Demo):**
- APAAR ID: `2024-MH-123456`
- Password: `2024-MH-123456`

## Usage Guide

### For Students

1. **Upload Certificate**
   - Navigate to "Upload Certificate"
   - Upload a file (image/PDF/DOCX) OR paste certificate text
   - Click "Extract & Open Form"
   - Watch the extraction progress

2. **Verify Auto-Filled Form**
   - Review auto-filled fields
   - Check confidence indicators
   - Edit any low-confidence fields (highlighted in yellow)
   - Fill in work description/logs for better matching

3. **Submit for Evaluation**
   - Click "Submit for Credit Evaluation"
   - If low-confidence fields exist, confirm submission
   - Wait for processing

4. **View Results**
   - See credit decision (Equivalent/Partially Equivalent/Not Equivalent)
   - View matched curriculum courses
   - Download PDF report
   - Check ABC registration status (if auto-pushed)

### For Mentors

1. **Login**
   - Navigate to "Mentor Login"
   - Use demo credentials

2. **Review Queue**
   - View submissions requiring review
   - Click "Review" on any submission

3. **Take Action**
   - Review extracted fields
   - Add custom keywords if needed
   - Push to ABC simulator

### For Students (ABC Portal Access)

1. **Access ABC/UGC Portal**
   - Click "ABC Portal Login" from home page
   - Or navigate to `/abc/login`

2. **Login**
   - Enter your APAAR ID (e.g., `2024-MH-123456`)
   - Enter password (default: same as APAAR ID)
   - Click "Login to ABC Portal"

3. **View Dashboard**
   - See your credit summary (total submissions, approved, total credits)
   - Browse all approved submissions
   - View details: internship info, credits awarded, ABC token, approval date
   - Download certificate/report PDFs

4. **Demo Account**
   - APAAR ID: `2024-MH-123456`
   - Password: `2024-MH-123456`
   - This account has 1 approved submission with 4 credits

**Note:** Student accounts are automatically created when a mentor approves and pushes a submission to ABC. The default password is set to the APAAR ID for demo purposes.

## Testing

### Run Extraction Tests
```bash
python tests/test_extract.py
```

This tests:
- Field extraction from sample certificate
- Confidence scoring
- File reading (TXT, PDF, DOCX)

### Run WMD Matching Tests
```bash
python tests/test_wmd.py
```

This tests:
- Curriculum matching for various domains
- Composite score calculation
- Decision classification
- Custom keyword addition

## Project Structure

```
.
├── app.py                      # Main Flask application
├── abc_portal.py               # ABC/UGC Portal Blueprint (NEW!)
├── extractor.py                # Certificate field extraction module
├── ceescm.py                   # CEESCM tokenization module
├── wmd_matcher.py              # WMD similarity matching module
├── report_generator.py         # PDF report generation
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── upload.html
│   ├── student_form.html
│   ├── mentor_login.html
│   ├── mentor_dashboard.html
│   ├── result.html
│   └── abc/                    # ABC Portal templates (NEW!)
│       ├── login.html          # Student login page
│       └── dashboard.html      # Student dashboard
│
├── static/                     # CSS and JavaScript
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── upload.js
│       └── student_form.js
│
├── uploads/                    # Data storage
│   ├── files/                  # Uploaded certificates
│   ├── db/                     # JSON records
│   │   ├── internships.json    # Internship submissions
│   │   ├── abc_records.json    # ABC approved submissions (NEW!)
│   │   └── abc_users.json      # ABC student accounts (NEW!)
│   ├── reports/                # Generated PDF reports
│   └── samples/                # Sample certificates
│       └── sample_cert_text.txt
│
└── tests/                      # Unit tests
    ├── test_extract.py
    └── test_wmd.py
```

## API Endpoints

### Student Endpoints
- `POST /api/upload_certificate` - Upload and extract certificate
- `GET /api/upload/{upload_id}` - Get upload metadata
- `POST /api/submit_internship` - Submit internship form
- `GET /api/internship/{id}` - Get internship record
- `DELETE /api/delete_data/{id}` - Delete student data
- `GET /api/download_report/{id}` - Download PDF report

### Mentor Endpoints
- `POST /api/mentor/login` - Mentor authentication
- `POST /api/mentor/logout` - Logout
- `POST /api/mentor/run_and_push` - Re-run matching and push to ABC

### ABC Simulator
- `POST /api/abc/upload` - Push to ABC simulator
- `GET /api/abc/status/{token}` - Check ABC status

## Configuration

### Environment Variables
- `SESSION_SECRET`: Flask session secret (defaults to dev key)

### Extraction Confidence Thresholds
- **High confidence**: ≥ 0.75 (auto-fill safe)
- **Medium confidence**: 0.50–0.74 (needs verification)
- **Low confidence**: < 0.50 (requires manual entry)

### Credit Calculation Rules
- **Equivalent**: 1 credit per 40 hours (max 4 credits)
- **Partially Equivalent**: 1 credit per 60 hours (max 2 credits)
- **Not Equivalent**: 0 credits

### WMD Decision Thresholds
- **Equivalent**: Composite score ≥ 0.70
- **Partially Equivalent**: 0.40 ≤ score < 0.70
- **Not Equivalent**: score < 0.40

## Curriculum Database

The system includes sample curriculum courses:
- CS301: Web Development Fundamentals
- CS302: Database Management Systems
- CS303: Machine Learning Basics
- CS304: Mobile App Development
- CS305: Cloud Computing
- CS306: Backend Development

**Note**: In production, replace with real curriculum data via database or API.

## Production Considerations

### Security
- Enable CSRF protection
- Use secure session secrets
- Implement proper authentication (replace hardcoded credentials)
- Add input validation and sanitization
- Use HTTPS

### Scaling
- Move from JSON files to PostgreSQL/MongoDB
- Add Redis for session management
- Implement async task queue (Celery) for OCR processing
- Use cloud storage (S3) for uploaded files

### ABC Integration
- Replace simulator with real ABC API
- Implement proper OAuth/API key management
- Add retry logic and error handling
- Log all ABC transactions

### Monitoring
- Add application logging (structured logs)
- Implement error tracking (Sentry)
- Add performance monitoring
- Create admin dashboard for analytics

## Troubleshooting

### Tesseract not found
- **Error**: `TesseractNotFoundError`
- **Solution**: Install Tesseract and add to PATH

### spaCy model not found
- **Error**: `OSError: [E050]`
- **Solution**: Run `pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl`

### PDF conversion fails
- **Error**: `PDFPageCountError` or `PDFSyntaxError`
- **Solution**: Install poppler-utils and ensure it's in PATH

### Low extraction accuracy
- **Cause**: Poor quality scanned images
- **Solution**: Use higher resolution scans (300 DPI+) or searchable PDFs

### Import errors
- **Solution**: Ensure all dependencies installed: `pip install -r requirements.txt`

## License

This is a demo application for educational purposes.

## Contact

For questions or issues, please refer to the documentation or create an issue in the project repository.

---

**Built with ❤️ for UGC Internship Credit Evaluation**
