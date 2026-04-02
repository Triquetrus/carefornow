# CareFor Now - System Architecture & Data Flow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CAREFOR NOW PLATFORM                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   PRESENTATION LAYER │
├──────────────────────┤
│ • Patient Dashboard  │
│ • Hospital Portal    │
│ • Funder Dashboard   │
│ • Admin Dashboard    │
│ • Track Status       │
│ • Payment Dashboard  │
└──────────────┬───────┘
               │
┌──────────────▼───────────────────────────┐
│         APPLICATION LAYER (Flask)        │
├─────────────────────────────────────────┤
│ • Authentication & Authorization        │
│ • Case Management Routes                │
│ • Document Processing                   │
│ • Funder Matching Algorithm             │
│ • Application Workflow                  │
│ • Payment Processing                    │
│ • Admin Functions                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│         DATA ACCESS LAYER (SQLAlchemy)   │
├─────────────────────────────────────────┤
│ • ORM Models                            │
│ • Database Transactions                 │
│ • Query Optimization                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼───────────────────────────┐
│      DATABASE LAYER (PostgreSQL/Supabase)│
├─────────────────────────────────────────┤
│ Tables:                                 │
│ • users (Patient, Hospital, Funder)     │
│ • cases (Case metadata)                 │
│ • documents (Uploaded files)            │
│ • applications (Funding requests)       │
│ • payments (Fund transfers)             │
└─────────────────────────────────────────┘

               ┌──────────────┐
               │  FILE STORAGE│
               ├──────────────┤
               │ • uploads/   │
               │   - Aadhar   │
               │   - Hosp.    │
               │   - Prescr.  │
               │   - Estimates│
               └──────────────┘
```

---

## 🔄 Complete Pipeline Flow Diagram

```
                        PATIENT JOURNEY
                        ═════════════════════

STEP 1: REGISTRATION & SETUP
┌─────────────────────────────────────┐
│ 1. Register as "family" user        │ → Route: /register
│ 2. Set bank details (CRITICAL)      │ → Route: /profile
│    - Account number                 │
│    - IFSC code                      │
│    - Account holder name            │
└─────────────────────────────────────┘
        │
        ▼
STEP 2: CASE CREATION
┌─────────────────────────────────────┐
│ 1. Fill case form (4 steps)         │ → Route: /new-case
│    - Patient info                   │
│    - Medical details                │
│    - Cost & urgency                 │
│    - Review                         │
│ 2. Submit case                      │
│ 3. Status: SUBMITTED                │ → Route: /funding-options
└─────────────────────────────────────┘
        │
        ▼
STEP 3: DOCUMENT UPLOAD (PATIENT SIDE)
┌─────────────────────────────────────┐
│ Patient uploads documents:          │ → Route: /case/{id}
│ ✓ Aadhar Card (ID proof)            │
│ ✓ Hospital Admission Letter         │
│ ✓ Cost Estimate                     │
│ ✓ Doctor's Prescription             │
│ ✓ Medical Records                   │
│ Status: DOCUMENTS_PENDING           │
└─────────────────────────────────────┘
        │
        ▼
STEP 4: HOSPITAL VERIFICATION
┌─────────────────────────────────────┐
│ Hospital Staff Reviews:             │ → Route: /hospital-dashboard
│ ✓ All uploaded documents            │ → /hospital/case/{id}
│ ✓ Verifies authenticity             │
│ ✓ Approves or requests changes      │
│ When ALL verified:                  │
│ Status: VERIFIED                    │
└─────────────────────────────────────┘
        │
        ▼
STEP 5: FUNDING APPLICATION
┌─────────────────────────────────────┐
│ 1. System matches best funders:     │ → Route: /funding-options
│    • Illness specialization         │
│    • Cost coverage capacity         │
│    • Processing speed               │
│    • Org type                       │
│ 2. Patient applies to best matches  │
│ 3. Application created              │
│ Status: VERIFIED (case)             │
└─────────────────────────────────────┘
        │
        ▼
STEP 6: FUNDER REVIEW & APPROVAL
┌─────────────────────────────────────┐
│ Funder Sees:                        │ → Route: /funder-dashboard
│ ✓ Patient details                   │ → /funder/review-application
│ ✓ All verified documents            │
│ ✓ Illness match %                   │
│ ✓ Cost & urgency                    │
│ ✓ Patient bank account              │
│                                     │
│ Funder Decides:                     │
│ ✓ APPROVE: Specify amount           │
│   (can be full or partial)          │
│ ✓ REJECT: Provide reason            │
│                                     │
│ If APPROVED:                        │
│ → Payment record created            │
│ → Status: APPROVED_FOR_FUNDING      │
│ → Amount: ₹450,000 (example)        │
└─────────────────────────────────────┘
        │
        ▼
STEP 7: PAYMENT PROCESSING
┌─────────────────────────────────────┐
│ Admin Reviews Pending Payments:     │ → Route: /admin-dashboard
│ • Patient bank account              │
│ • Approved amount                   │
│ • Funder details                    │
│                                     │
│ Admin Releases Payment:             │
│ → Verifies all details correct      │
│ → Clicks "Release Payment"          │
│ → Payment status: COMPLETED         │
│ → Status: FUNDED                    │
└─────────────────────────────────────┘
        │
        ▼
STEP 8: FUND TRANSFER
┌─────────────────────────────────────┐
│ Patient Receives Funds:             │
│ • Bank account: HDFC Bank           │
│ • Amount: ₹450,000                  │
│ • Transaction ID: TXN...            │
│ • Status: Released                  │
│                                     │
│ Patient Notification:               │
│ ✓ Email confirmation                │
│ ✓ SMS alert (optional)              │
│ ✓ Dashboard update                  │
└─────────────────────────────────────┘
        │
        ▼
STEP 9: TRACKING & CONFIRMATION
┌─────────────────────────────────────┐
│ Patient Can:                        │ → Route: /track-status
│ ✓ See complete pipeline             │ → /my-funding
│ ✓ View payment status               │
│ ✓ Download documents                │
│ ✓ Access transaction details        │
│ ✓ Check bank transfer status        │
└─────────────────────────────────────┘

                        ✅ FUNDING COMPLETE ✅
```

---

## 📊 Database Relationship Diagram

```
                       users
        ┌──────────────┬───────────────┐
        │              │               │
        │         (user_id)       (user_id)
        │              │               │
        ▼              ▼               ▼
    cases        documents       applications
        │              │               │
        │         (case_id)       (case_id)
        │              │               │
        └──────────────┼───────────────┘
                       │
                  (case_id)
                       │
                       ▼
                   payments

                (fund_transfers)
        ┌──────────────────────────┐
        │   Bank Account Details   │
        │   • account_number       │
        │   • account_holder       │
        │   • bank_name            │
        │   • ifsc_code            │
        │   • transaction_id       │
        └──────────────────────────┘
```

---

## 🔐 Data Flow - Document Upload & Verification

```
PATIENT UPLOADS DOCUMENT
├─ File sent to server
├─ Scanned for virus (future)
├─ Saved to: uploads/{case_id}_{doc_type}_{filename}
├─ Entry created in documents table
│  ├─ id: UUID
│  ├─ case_id: references cases.id
│  ├─ user_id: patient's user id
│  ├─ doc_type: aadhar, hospital_letter, etc
│  ├─ file_path: path on disk
│  ├─ file_size: bytes
│  ├─ verified: False (initially)
│  └─ created_at: timestamp
└─ Case status → documents_pending
   └─ Notification: Hospital can now verify

HOSPITAL REVIEWS DOCUMENT
├─ Hospital staff views document
├─ Can approve ✓ or request changes ✗
├─ If approved:
│  ├─ verified = True
│  ├─ verified_by = hospital_user_id
│  ├─ verified_at = timestamp
│  └─ Check if ALL docs verified
│     └─ If yes: case.status → verified
├─ If rejected:
│  ├─ verified = False
│  ├─ rejection_reason = "reason text"
│  └─ Notification: Patient can resubmit
└─ Patient can download/view document

FUNDER REVIEWS DOCUMENTS
├─ Funder sees all verified documents ✓
├─ Can review document details
├─ Can download document
├─ Visible in application review page
└─ Used to make approval decision

VISIBILITY MATRIX:
┌──────────────────────────────────────────┐
│ Document Type  │ Patient │ Hospital │ Funder │
├──────────────────────────────────────────┤
│ Aadhar Card    │   ✓    │    ✓     │   ✓    │
│ Hosp Letter    │   ✓    │    ✓     │   ✓    │
│ Cost Est.      │   ✓    │    ✓     │   ✓    │
│ Medical Rec.   │   ✓    │    ✓     │   ✓    │
│ Bank Proof     │   ✓    │    ✗     │   ✗    │
└──────────────────────────────────────────┘
```

---

## 💰 Payment Flow Diagram

```
FUNDER APPROVAL
───────────────

Funder Reviews Case
├─ Patient info
├─ Verified documents
├─ Illness match
└─ Bank account for transfer

Funder Makes Decision
├─ APPROVE:
│  ├─ Specify amount (₹450,000)
│  ├─ Add optional note
│  └─ Click "Submit Decision"
│
├─ REJECT:
│  ├─ Provide rejection reason
│  └─ Click "Submit Decision"
└─ Application status → approved/rejected

IF APPROVED: PAYMENT RECORD CREATED
───────────────────────────────────

CREATE PAYMENT RECORD:
├─ id: UUID
├─ case_id: from case
├─ user_id: patient's user id
├─ total_amount: ₹450,000 (funder's approval)
├─ released_amount: 0 (initially)
├─ status: processing
├─ bank_name: "HDFC Bank" (from user profile)
├─ account_number: "1234567890123456"
├─ ifsc_code: "HDFC0001234"
├─ account_holder: "Ramesh Kumar"
├─ transaction_id: "TXN..." (auto-generated)
├─ reference_id: "REF..." (case reference)
└─ Case status → approved_for_funding

ADMIN PAYMENT RELEASE
─────────────────────

Admin Sees Payment in Dashboard:
├─ Patient name
├─ Case ID
├─ Amount: ₹450,000
├─ Status: Processing
├─ Bank details
│  ├─ Account holder
│  ├─ Account number (last 4 digits)
│  ├─ IFSC code
│  └─ Bank name
├─ Transaction ID
└─ Release Payment button

Admin Clicks "Release Payment":
├─ Verify all details correct
├─ Click confirm
│
└─ Update Payment Record:
   ├─ status: completed
   ├─ released_at: datetime.now()
   ├─ released_amount: 450,000
   │
   ├─ Case status → funded
   │
   └─ Notifications Sent:
      ├─ Patient: "Your funds have been released"
      ├─ Hospital: "Case funding completed"
      └─ Funder: "Payment released successfully"

PATIENT SEES RESULTS
────────────────────

Track Status Page (/track-status):
├─ 📤 Submitted ✓
├─ 📁 Documents ✓
├─ ✅ Hospital Verified ✓
├─ 💼 Funder Approved ✓
└─ 🎉 Funding Received ✓

My Funding Page (/my-funding):
├─ Payment Status: Released ✓
├─ Amount: ₹450,000
├─ Bank: HDFC Bank
├─ Account: ...3456
├─ Transaction: TXN...
└─ Released Date: 2024-03-28
```

---

## 🎯 Role-Based Access Control Matrix

```
┌────────────────────────────────────────────────────────────┐
│                    PERMISSION MATRIX                        │
├─────────────────┬──────────┬──────────┬────────┬───────────┤
│    Action       │ Patient  │ Hospital │ Funder │   Admin   │
├─────────────────┼──────────┼──────────┼────────┼───────────┤
│ Register        │    ✓     │    ✓     │   ✓    │     ✓     │
│ View own profile│    ✓     │    ✓     │   ✓    │     ✓     │
│ Edit own profile│    ✓     │    ✓     │   ✓    │     ✓     │
│ Create case     │    ✓     │    ✗     │   ✗    │     ✗     │
│ View own cases  │    ✓     │    ✗     │   ✗    │     ✗     │
│ Upload docs     │    ✓     │    ✗     │   ✗    │     ✗     │
│ View uploaded   │    ✓     │    ✓     │   ✓    │     ✓     │
│ Verify docs     │    ✗     │    ✓     │   ✗    │     ✗     │
│ Apply for fund  │    ✓     │    ✗     │   ✗    │     ✗     │
│ Review app      │    ✗     │    ✗     │   ✓    │     ✗     │
│ Approve funding │    ✗     │    ✗     │   ✓    │     ✗     │
│ Track status    │    ✓     │    ✗     │   ✗    │     ✗     │
│ Release payment │    ✗     │    ✗     │   ✗    │     ✓     │
│ View all cases  │    ✗     │    ✗     │   ✗    │     ✓     │
│ Admin dashboard │    ✗     │    ✗     │   ✗    │     ✓     │
└─────────────────┴──────────┴──────────┴────────┴───────────┘
```

---

## 🔀 Status Transition Diagram

```
START
  │
  ▼
SUBMITTED (Patient creates case)
  │
  ├─→ Patient uploads documents
  │
  ▼
DOCUMENTS_PENDING (Hospital can review)
  │
  ├─→ Hospital verifies docs
  │
  ├─→ OR Hospital rejects (patient resubmits)
  │
  ▼
VERIFIED (All docs approved by hospital)
  │
  ├─→ Patient applies to funders
  │
  ├─→ Application created
  │
  ▼
VERIFIED (Waiting for funder decision)
  │
  ├─→ Funder approves + specifies amount
  │   └─→ Payment record created
  │
  │ ├─→ OR Funder rejects
  │       └─→ Application rejected (patient can reapply)
  │
  ▼
APPROVED_FOR_FUNDING (Admin can release)
  │
  ├─→ Admin releases payment
  │
  ▼
FUNDED (Patient receives funds) ✓
  │
  └─→ END


Status Flow:
submitted → documents_pending → verified → approved_for_funding → funded

Possible Branches:
✓ Success path (shown above)
✓ Rejection path (documents rejected, can resubmit)
✓ Funding rejection path (can apply to different funder)
```

---

## 🌐 API Endpoint Summary

```
Authentication
├─ POST /register          - User registration
├─ POST /login             - User login
└─ GET /logout             - User logout

Patient Routes
├─ GET /dashboard          - Patient dashboard
├─ GET /profile            - View/edit bank details
├─ POST /profile           - Save bank details
├─ GET /new-case           - Case creation form
├─ POST /emergency-case    - Submit case
├─ GET /case/{id}          - View case + upload docs
├─ POST /upload-document   - Upload file
├─ GET /download-document/{id} - Download file
├─ GET /funding-options/{id}   - View matched funders
├─ POST /apply-funding     - Apply to funder
├─ GET /track-status/{id}  - Real-time tracking
└─ GET /my-funding         - Payment dashboard

Hospital Routes
├─ GET /hospital-dashboard - Cases pending verification
├─ GET /hospital/case/{id} - Review case + docs
└─ POST /hospital/verify-documents - Verify/reject doc

Funder Routes
├─ GET /funder-dashboard   - All verified cases
├─ GET /funder/review-application/{id} - Review application
└─ POST /funder/respond    - Approve/reject with amount

Admin Routes
├─ GET /admin-dashboard    - Admin dashboard
└─ POST /admin/release-payment/{id} - Release funds

API Endpoints
├─ GET /api/user           - Current user info
├─ GET /api/case/{id}      - Case details
├─ GET /api/case/{id}/documents   - Case documents
└─ GET /api/case/{id}/applications - Case applications
```

---

## 📈 Database Growth Projection

```
With 1000 patients creating cases:

users table:              ~4,000 records (1000 patients + hospitals + funders + admin)
cases table:              ~1,500 records (avg 1.5 cases per patient)
documents table:          ~7,500 records (avg 5 docs per case)
applications table:       ~4,500 records (avg 3 funders per case)
payments table:           ~1,200 records (avg 80% success rate)

Total database size:      ~50-100 MB (with file metadata)
File storage size:        ~1-2 GB (depending on document sizes)
```

---

## 🔒 Security Considerations

```
Authentication:
✓ Flask sessions with secure cookies
✓ Password hashing (future enhancement)
✓ Session timeout protection

Authorization:
✓ Role-based access control (@role_required decorator)
✓ User ID verification on all actions
✓ Endpoint authorization checks

Data Security:
✓ Bank details encrypted at rest (future)
✓ File uploads scanned for malware (future)
✓ HTTPS in production
✓ SQL injection prevention (SQLAlchemy ORM)

File Security:
✓ Secure filename generation
✓ File type validation
✓ File size limits (50MB)
✓ Upload folder isolation

Session Security:
✓ Session-based authentication
✓ CSRF protection (future)
✓ Rate limiting (future)
```

---

**Architecture Document Complete ✓**

For implementation, refer to IMPLEMENTATION_GUIDE.md and QUICK_START.md.
