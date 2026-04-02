# CareFor Now - Complete Pipeline Implementation Guide

## 🎯 Project Overview

**CareFor Now** is a complete healthcare funding platform with an end-to-end pipeline from patient case submission to fund transfer.

### Complete Pipeline Flow:
```
1. PATIENT REGISTRATION & PROFILE SETUP
   ↓
2. CASE CREATION (with patient details, medical info, cost, urgency)
   ↓
3. DOCUMENT UPLOAD & VERIFICATION (by hospital staff)
   ↓
4. FUNDING APPLICATION (to matched NGOs/CSR/Insurance)
   ↓
5. FUNDER APPROVAL (with specific amount)
   ↓
6. PAYMENT PROCESSING (by admin)
   ↓
7. FUND TRANSFER (to patient's bank account)
```

---

## 📁 File Structure

```
carefor-now/
├── app.py                          # Main Flask application (UPDATED - COMPLETE PIPELINE)
├── requirements.txt                # Python dependencies
├── uploads/                        # Document storage folder
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── dashboard.html             # Patient dashboard
│   ├── profile.html               # [NEW] Bank details & profile
│   ├── emergency_case.html        # Case creation form
│   ├── case_detail.html           # [NEW] Case with document upload
│   ├── funding_options.html       # Available funders
│   ├── track_status.html          # [NEW] Real-time pipeline tracking
│   ├── my_funding.html            # [NEW] Payment dashboard
│   ├── hospital_dashboard.html    # Hospital staff dashboard
│   ├── hospital_case_detail.html  # [NEW] Hospital verification page
│   ├── funder_dashboard.html      # Funder staff dashboard
│   ├── funder_review_application.html  # [NEW] Funder approval page
│   ├── admin_dashboard.html       # Admin dashboard (with payment release)
│   ├── 404.html                   # Error page
│   └── 500.html                   # Error page
```

---

## 🔄 Complete Data Flow

### 1. USER REGISTRATION
- Users register as: **family** (patient), **hospital**, **funder**, or **admin**
- Family users get dashboard to create cases

### 2. PATIENT PROFILE SETUP (NEW)
**Route:** `/profile`

**Patient adds bank details for receiving funds:**
- Bank Name (e.g., HDFC Bank)
- Account Number
- Account Holder Name (as per bank records)
- IFSC Code

**Why:** Funds are transferred here when funder approves.

### 3. CASE CREATION
**Route:** `/new-case` → `/emergency-case`

**Patient submits case with:**
- Patient name, age, gender
- Illness type (from predefined list)
- Hospital name & location
- Estimated treatment cost
- Urgency level (Critical/High/Medium)
- Description of situation

**Status:** `submitted`

### 4. DOCUMENT UPLOAD (NEW)
**Route:** `/case/<case_id>`

**Patient uploads required documents:**
- ✅ Aadhar Card (ID proof) - visible to funders
- ✅ Hospital Admission Letter
- ✅ Cost Estimate from hospital
- ✅ Doctor's Prescription
- ✅ Medical Records (if available)
- ✅ Bank proof (optional)

**Case Status:** `documents_pending`

**Database:** `Document` table stores:
- doc_type, file_path, file_size
- verified (True/False)
- rejection_reason (if resubmitted)

### 5. HOSPITAL VERIFICATION (NEW)
**Route:** `/hospital-dashboard` → `/hospital/case/<case_id>`

**Hospital staff reviews documents:**
- Views each uploaded document
- Can approve ✅ or request changes ❌
- When all documents verified → case marked `verified`

**Case Status:** `verified`

**Database Updates:**
- Document.verified = True
- Document.verified_by = hospital_user_id
- Document.verified_at = datetime

### 6. FUNDING APPLICATION
**Route:** `/funding-options/<case_id>`

**Patient sees matched funders** (scored by):
- Illness specialization match (40 pts)
- Cost within funder's max limit (25 pts)
- Urgency vs processing speed (20 pts)
- Org type bonus (15 pts)

**Patient applies to best-matched funders:**
- Application created with status `submitted`
- Case moves to `verified` status

**Case Status:** `verified` (after documents verified)

### 7. FUNDER REVIEW & APPROVAL (NEW)
**Route:** `/funder-dashboard` → `/funder/review-application/<app_id>`

**Funder sees:**
- Complete case details
- All hospital-verified documents
- Patient bank information
- Illness match with their specialization

**Funder can:**
- ✅ **Approve** - specify funding amount (full or partial)
  - Example: Patient asked ₹500,000, funder approves ₹400,000
  - `Application.status = 'approved'`
  - `Application.amount_offered = 400000`
  - Creates `Payment` record with status `processing`
  - `Case.status = 'approved_for_funding'`

- ❌ **Reject** - provide rejection reason
  - `Application.status = 'rejected'`
  - `Application.note = reason`

**Payment Record Created:**
```python
Payment(
    case_id = case.id,
    user_id = patient_id,
    total_amount = 400000,  # Amount funder approved
    released_amount = 0,
    status = 'processing',  # Will be released by admin
    bank_name = patient.bank_name,
    account_number = patient.account_number,
    ifsc_code = patient.ifsc_code,
    account_holder = patient.account_holder,
    transaction_id = 'TXN...',  # Auto-generated
    reference_id = 'REF...'     # Auto-generated
)
```

### 8. ADMIN PAYMENT RELEASE (NEW)
**Route:** `/admin-dashboard`

**Admin reviews all pending payments:**
- See all cases in `approved_for_funding` status
- Check patient bank details
- Release payment with one click

**When Payment Released:**
- `Payment.status = 'completed'`
- `Payment.released_at = datetime.utcnow()`
- `Payment.released_amount = total_amount`
- `Case.status = 'funded'` ✅

**Simulated Flow:**
- In real system: triggers bank API to transfer funds
- For demo: marks as completed (actual transfer would be via payment gateway)

### 9. PATIENT TRACKING (NEW)
**Route:** `/track-status/<case_id>`

**Real-time pipeline visualization:**
```
📤 Submitted → 📁 Documents → ✅ Hospital Verified → 💼 Funder Approved → 🎉 Funded
```

**Shows:**
- Current status with timestamp
- Document verification status
- Application status from each funder
- Payment details (if approved)
- Next steps

**Auto-refreshes every 30 seconds** to show live updates.

### 10. PAYMENT DASHBOARD (NEW)
**Route:** `/my-funding`

**Patient sees:**
- Summary: Total cases, funded cases, total received amount
- All their cases with status
- Payment tracking with:
  - Total amount approved
  - Released amount
  - Bank account (masked)
  - Transaction ID
  - Release date

---

## 🗄️ Database Schema

### Users Table (Enhanced)
```sql
users
├── id (String)
├── email (String, unique)
├── name (String)
├── phone (String)
├── user_type (String) -- family|hospital|funder|admin
├── bank_name (String) -- NEW
├── account_number (String) -- NEW
├── ifsc_code (String) -- NEW
├── account_holder (String) -- NEW
└── created_at (DateTime)
```

### Cases Table (Enhanced)
```sql
cases
├── id (String)
├── user_id (FK → users.id)
├── patient_name (String)
├── age (Integer)
├── gender (String)
├── illness_type (String)
├── hospital_name (String)
├── hospital_location (String)
├── estimated_cost (Integer)
├── urgency (Integer) -- 1:Critical, 2:High, 3:Medium
├── description (Text)
├── status (String) -- submitted|documents_pending|verified|approved_for_funding|funded
├── verified_by (String) -- hospital user_id
├── verified_at (DateTime) -- NEW
├── approved_by (String) -- funder user_id -- NEW
├── approved_at (DateTime) -- NEW
└── created_at (DateTime)
```

### Documents Table (NEW)
```sql
documents
├── id (String)
├── case_id (FK → cases.id)
├── user_id (FK → users.id)
├── doc_type (String) -- aadhar|hospital_letter|cost_estimate|etc
├── file_name (String)
├── file_path (String)
├── file_size (Integer)
├── verified (Boolean) -- Hospital approval
├── verified_by (String) -- hospital user_id
├── verified_at (DateTime)
├── rejection_reason (Text) -- If hospital rejects
└── created_at (DateTime)
```

### Applications Table
```sql
applications
├── id (String)
├── case_id (FK → cases.id)
├── user_id (FK → users.id)
├── org_id (String) -- Funder ID
├── org_name (String)
├── status (String) -- submitted|approved|rejected
├── amount_offered (Integer) -- NEW: Amount funder approved
├── note (Text) -- Funder's note
├── created_at (DateTime)
└── updated_at (DateTime)
```

### Payments Table (NEW)
```sql
payments
├── id (String)
├── case_id (FK → cases.id)
├── user_id (FK → users.id)
├── total_amount (Integer) -- Amount approved by funder
├── released_amount (Integer) -- Amount transferred
├── status (String) -- pending|processing|completed
├── bank_name (String) -- Copied from user at approval
├── account_number (String)
├── ifsc_code (String)
├── account_holder (String)
├── transaction_id (String) -- Unique identifier
├── reference_id (String) -- Case reference
├── created_at (DateTime)
└── released_at (DateTime) -- When admin released it
```

---

## 🛣️ Key API Endpoints

### Patient Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/profile` | GET/POST | Update bank details |
| `/new-case` | GET | Case creation form |
| `/emergency-case` | POST | Submit case |
| `/case/<case_id>` | GET | Case details + document upload |
| `/upload-document` | POST | Upload document |
| `/download-document/<doc_id>` | GET | Download document |
| `/funding-options/<case_id>` | GET | View matched funders |
| `/apply-funding` | POST | Apply to funder |
| `/track-status/<case_id>` | GET | Real-time pipeline tracking |
| `/my-funding` | GET | Payment dashboard |

### Hospital Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/hospital-dashboard` | GET | Cases pending verification |
| `/hospital/case/<case_id>` | GET | Review documents |
| `/hospital/verify-documents` | POST | Approve/reject document |

### Funder Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/funder-dashboard` | GET | All verified cases + applications |
| `/funder/review-application/<app_id>` | GET | Review application |
| `/funder/respond` | POST | Approve/reject with amount |

### Admin Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/admin-dashboard` | GET | All stats + payment release |
| `/admin/release-payment/<payment_id>` | POST | Release funds to patient |

---

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
pip install flask flask-sqlalchemy werkzeug
```

### 2. Update `app.py`
Replace the original `app.py` with the complete version provided.

### 3. Create Folders
```bash
mkdir -p uploads
mkdir -p static/css static/js
```

### 4. Database Setup
```bash
python3
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
```

### 5. Add Templates
Copy all provided HTML templates to `templates/` folder:
- `profile.html`
- `case_detail.html`
- `hospital_case_detail.html`
- `funder_review_application.html`
- `track_status.html`
- `my_funding.html`

### 6. Run Server
```bash
python app.py
```

Visit: http://localhost:5000

---

## 👥 Test Accounts

### Patient/Family
- Email: `patient@carefor.com`
- Click Register → family user

### Hospital
- Email: `hospital@carefor.com`
- Click Register → hospital user

### Funder
- Email: `funder@carefor.com`
- Click Register → funder user

### Admin
- Email: `admin@carefor.com`
- Click Register → admin user

---

## 📊 Testing the Complete Pipeline

### Step 1: Patient Setup
1. Register as "family" user
2. Go to `/profile` → Add bank details
3. Go to `/new-case` → Create case
4. Go to `/case/<id>` → Upload documents (Aadhar, hospital letter, etc.)

### Step 2: Hospital Verification
1. Register as "hospital" user
2. Go to `/hospital-dashboard`
3. Click pending case → Review documents
4. Approve all documents → Case becomes `verified`

### Step 3: Funding Application
1. Back as patient
2. Go to `/funding-options/<case_id>`
3. Click "Apply" on best-matched funder
4. Case moves to funding queue

### Step 4: Funder Approval
1. Register as "funder" user
2. Go to `/funder-dashboard`
3. Click application to review
4. Approve with specific amount (e.g., ₹400,000)
5. Payment record created

### Step 5: Payment Release
1. Register as "admin" user
2. Go to `/admin-dashboard`
3. See pending payment
4. Click "Release Payment"
5. Case status → `funded` ✅
6. Patient's bank marked for transfer

### Step 6: Track Progress
1. Back as patient
2. Go to `/my-funding` → See payment details
3. Go to `/track-status/<case_id>` → See pipeline progress

---

## 🔐 Security Notes

1. **Bank Details**: Stored encrypted (use SQLAlchemy encryption in production)
2. **Document Files**: Stored in uploads folder (implement virus scanning)
3. **Payment Transactions**: In demo, simulated. Use Razorpay/Stripe API in production
4. **Authorization**: Role-based access control on all endpoints
5. **Session Management**: Flask sessions (use secure cookies in production)

---

## 📈 Future Enhancements

1. **Payment Gateway Integration**: Connect to Razorpay/Stripe for actual transfers
2. **Email Notifications**: Send updates at each pipeline stage
3. **SMS Alerts**: For critical milestones
4. **Document Scanning**: OCR for document verification
5. **Analytics Dashboard**: Funder success rates, average funding time
6. **Appeals Process**: Patients can appeal rejected applications
7. **Partial Funding**: Multiple funders can contribute to one case
8. **Milestone Tracking**: Release funds in phases based on treatment progress

---

## 🎯 Key Features Implemented

✅ Complete user authentication (4 roles)
✅ Case creation with full details
✅ Document upload & management
✅ Hospital verification workflow
✅ Intelligent funder matching algorithm
✅ Funder approval with variable amounts
✅ Bank details management
✅ Payment processing pipeline
✅ Real-time status tracking
✅ Admin payment release
✅ Payment dashboard
✅ Role-based access control
✅ Error handling & validation

---

## 📞 Support

For issues or questions about the implementation, refer to the code comments and docstrings in `app.py`.

---

**Happy Funding! 🎉**
