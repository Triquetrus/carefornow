from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.secret_key = 'carefor_now_secret_key_2024'

# ============================================================
#  DATABASE — Supabase
# ============================================================
SUPABASE_URI = "postgresql://postgres.ixvgwrgggedzurleeucv:CareForNow2026@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File uploads
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

db = SQLAlchemy(app)


# ============================================================
#  MODELS
# ============================================================

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.String(50),  primary_key=True)
    email      = db.Column(db.String(200), unique=True, nullable=False)
    name       = db.Column(db.String(200))
    phone      = db.Column(db.String(20))
    user_type  = db.Column(db.String(50),  nullable=False)  # family | hospital | funder | admin
    
    # Bank details (for patient/family to receive funds)
    bank_name  = db.Column(db.String(200))
    account_number = db.Column(db.String(50))
    ifsc_code  = db.Column(db.String(20))
    account_holder = db.Column(db.String(200))
    
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    cases        = db.relationship('Case',        backref='user', lazy=True)
    applications = db.relationship('Application', backref='user', lazy=True)
    documents    = db.relationship('Document',    backref='user', lazy=True)
    payments     = db.relationship('Payment',     backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'email': self.email,
            'name': self.name, 'phone': self.phone, 'user_type': self.user_type,
            'bank_name': self.bank_name,
            'account_holder': self.account_holder,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }


class Case(db.Model):
    __tablename__ = 'cases'
    id                = db.Column(db.String(50),  primary_key=True)
    user_id           = db.Column(db.String(50),  db.ForeignKey('users.id'), nullable=False)
    patient_name      = db.Column(db.String(200), nullable=False)
    age               = db.Column(db.Integer)
    gender            = db.Column(db.String(20))
    illness_type      = db.Column(db.String(100))
    hospital_name     = db.Column(db.String(200))
    hospital_location = db.Column(db.String(200))
    estimated_cost    = db.Column(db.Integer,     default=0)
    urgency           = db.Column(db.Integer,     default=3)  # 1=Critical 2=High 3=Medium
    description       = db.Column(db.Text)
    
    # Status flow: submitted → documents_pending → verified → approved_for_funding → funded → payment_released
    status            = db.Column(db.String(50),  default='submitted')
    
    verified_by       = db.Column(db.String(50),  nullable=True)   # hospital user id
    verified_at       = db.Column(db.DateTime,    nullable=True)
    
    approved_by       = db.Column(db.String(50),  nullable=True)   # funder user id
    approved_at       = db.Column(db.DateTime,    nullable=True)
    
    created_at        = db.Column(db.DateTime,    default=datetime.utcnow)

    applications = db.relationship('Application', backref='case', lazy=True)
    documents    = db.relationship('Document',    backref='case', lazy=True)
    payment      = db.relationship('Payment',     backref='case', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'patient_name': self.patient_name,
            'age': self.age,
            'gender': self.gender,
            'illness_type': self.illness_type,
            'hospital_name': self.hospital_name,
            'hospital_location': self.hospital_location,
            'estimated_cost': self.estimated_cost,
            'urgency': self.urgency,
            'description': self.description,
            'status': self.status,
            'verified_at': self.verified_at.strftime('%Y-%m-%d %H:%M') if self.verified_at else '',
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }


class Document(db.Model):
    __tablename__ = 'documents'
    id            = db.Column(db.String(50),  primary_key=True)
    case_id       = db.Column(db.String(50),  db.ForeignKey('cases.id'), nullable=False)
    user_id       = db.Column(db.String(50),  db.ForeignKey('users.id'), nullable=False)
    
    doc_type      = db.Column(db.String(100))  # aadhar, hospital_letter, cost_estimate, medical_records, bank_proof
    file_name     = db.Column(db.String(500))
    file_path     = db.Column(db.String(500))
    file_size     = db.Column(db.Integer)  # in bytes
    
    # Verification by hospital
    verified      = db.Column(db.Boolean, default=False)
    verified_by   = db.Column(db.String(50))  # hospital user id
    verified_at   = db.Column(db.DateTime)
    
    rejection_reason = db.Column(db.Text)
    
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'doc_type': self.doc_type,
            'file_name': self.file_name,
            'verified': self.verified,
            'verified_by': self.verified_by,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


class Application(db.Model):
    __tablename__ = 'applications'
    id         = db.Column(db.String(50), primary_key=True)
    case_id    = db.Column(db.String(50), db.ForeignKey('cases.id'),  nullable=False)
    user_id    = db.Column(db.String(50), db.ForeignKey('users.id'),  nullable=False)
    org_id     = db.Column(db.String(50), nullable=False)
    org_name   = db.Column(db.String(200))
    status     = db.Column(db.String(50), default='submitted')   # submitted | approved | rejected
    note       = db.Column(db.Text)
    amount_offered = db.Column(db.Integer)  # Amount funder is willing to give
    created_at = db.Column(db.DateTime,  default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,  default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'org_id': self.org_id,
            'org_name': self.org_name,
            'status': self.status,
            'amount_offered': self.amount_offered,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else ''
        }


class Payment(db.Model):
    __tablename__ = 'payments'
    id            = db.Column(db.String(50), primary_key=True)
    case_id       = db.Column(db.String(50), db.ForeignKey('cases.id'), nullable=False)
    user_id       = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    total_amount  = db.Column(db.Integer)  # Total approved funding
    released_amount = db.Column(db.Integer, default=0)
    
    # Payment status: pending → processing → completed
    status        = db.Column(db.String(50), default='pending')
    
    # Bank details (copied from user at time of approval)
    bank_name     = db.Column(db.String(200))
    account_number = db.Column(db.String(50))
    ifsc_code     = db.Column(db.String(20))
    account_holder = db.Column(db.String(200))
    
    # Transaction ID
    transaction_id = db.Column(db.String(100), unique=True)
    
    # Reference
    reference_id  = db.Column(db.String(100))
    
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    released_at   = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'total_amount': self.total_amount,
            'released_amount': self.released_amount,
            'status': self.status,
            'account_holder': self.account_holder,
            'bank_name': self.bank_name,
            'transaction_id': self.transaction_id,
            'reference_id': self.reference_id,
            'released_at': self.released_at.strftime('%Y-%m-%d %H:%M') if self.released_at else '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }


# ============================================================
#  STATIC DATA
# ============================================================

SAMPLE_FUNDING_ORGS = [
    {
        "id": "ngo_001", "name": "LifeCare Foundation", "type": "NGO",
        "location": "Mumbai",
        "specializations": ["Cancer", "Heart Disease", "Emergency Care", "Heart Surgery"],
        "max_funding": 500000, "processing_time": "2-3 days", "verified": True, "logo": "🏥"
    },
    {
        "id": "csr_001", "name": "Corporate Health Initiative", "type": "CSR Fund",
        "location": "Pune",
        "specializations": ["Emergency Surgery", "Critical Illness", "Accident/Trauma"],
        "max_funding": 1000000, "processing_time": "1-2 days", "verified": True, "logo": "🏢"
    },
    {
        "id": "gov_001", "name": "Ayushman Bharat Scheme", "type": "Government",
        "location": "All India",
        "specializations": ["Cancer", "Heart Disease", "Kidney Disease", "Neurological Disorder"],
        "max_funding": 500000, "processing_time": "3-5 days", "verified": True, "logo": "🏛️"
    },
    {
        "id": "ins_001", "name": "Health Plus Insurance", "type": "Insurance",
        "location": "Pan India",
        "specializations": ["Cancer", "Heart Disease", "Emergency Surgery", "Accident/Trauma",
                            "Kidney Disease", "Diabetes", "Critical Illness", "Burn Injury",
                            "Neurological Disorder", "Respiratory Issues"],
        "max_funding": 2000000, "processing_time": "2-4 days", "verified": True, "logo": "📋"
    }
]

ILLNESS_TYPES = [
    "Cancer", "Heart Disease", "Emergency Surgery", "Accident/Trauma",
    "Kidney Disease", "Diabetes", "Critical Illness", "Burn Injury",
    "Neurological Disorder", "Respiratory Issues"
]

DOCUMENT_TYPES = [
    ("aadhar", "Aadhar Card (ID Proof)"),
    ("hospital_letter", "Hospital Admission Letter"),
    ("cost_estimate", "Hospital Cost Estimate"),
    ("doctor_prescription", "Doctor's Prescription"),
    ("bank_proof", "Bank Account Proof"),
    ("medical_records", "Previous Medical Records"),
    ("income_certificate", "Income Certificate")
]


# ============================================================
#  MATCHING ALGORITHM
# ============================================================

def match_funding_sources(case_data):
    """Score each funding org"""
    urgency        = int(case_data.get('urgency', 3))
    required_cost  = int(case_data.get('estimated_cost', 0))
    illness        = str(case_data.get('illness_type', ''))

    results = []
    for org in SAMPLE_FUNDING_ORGS:
        score = 0
        if illness in org['specializations']:
            score += 40
        elif any(s.lower() in illness.lower() for s in org['specializations']):
            score += 20
        if required_cost <= org['max_funding']:
            coverage = min(org['max_funding'] / max(required_cost, 1), 2)
            score += int(25 * min(coverage / 2, 1))
        pt = org['processing_time']
        if urgency == 1:
            if pt.startswith('1-2'):   score += 20
            elif pt.startswith('2-3'): score += 12
            else:                      score += 4
        elif urgency == 2:
            if pt.startswith('1-2'):   score += 16
            elif pt.startswith('2-3'): score += 20
            else:                      score += 8
        else:
            score += 15
        if urgency == 1 and org['type'] == 'CSR Fund':   score += 10
        if urgency <= 2 and org['type'] == 'Insurance':  score += 5
        score = min(score, 100)
        results.append({
            **org,
            'match_score': score,
            'relevance': 'Highly Relevant' if score >= 70 else 'Relevant' if score >= 45 else 'Standard'
        })
    return sorted(results, key=lambda x: x['match_score'], reverse=True)


# ============================================================
#  DECORATORS
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('user_type') != role:
                return render_template('unauthorized.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================
#  AUTH ROUTES
# ============================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        user_type = data.get('user_type', 'family')
        password = data.get('password', '')
        
        if not email or not name:
            return jsonify({'success': False, 'message': 'Email and name required'})
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            phone=phone,
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        
        return jsonify({'success': True, 'message': 'Registration successful'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
        
        session['user_id'] = user.id
        session['user_type'] = user.user_type
        
        return jsonify({'success': True, 'user_type': user.user_type})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ============================================================
#  ROUTES — PATIENT/FAMILY
# ============================================================

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    if user.user_type == 'family':
        user_cases = Case.query.filter_by(user_id=session['user_id']).order_by(Case.created_at.desc()).all()
        return render_template('dashboard.html', user=user, user_cases=user_cases)
    elif user.user_type == 'hospital':
        return redirect(url_for('hospital_dashboard'))
    elif user.user_type == 'funder':
        return redirect(url_for('funder_dashboard'))
    elif user.user_type == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html', user=user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        data = request.get_json()
        user.name = data.get('name', user.name)
        user.phone = data.get('phone', user.phone)
        user.bank_name = data.get('bank_name')
        user.account_number = data.get('account_number')
        user.ifsc_code = data.get('ifsc_code')
        user.account_holder = data.get('account_holder')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated'})
    return render_template('profile.html', user=user)

@app.route('/emergency-case', methods=['POST'])
@login_required
def emergency_case():
    data = request.get_json()
    case = Case(
        id=str(uuid.uuid4()),
        user_id=session['user_id'],
        patient_name=data.get('patient_name'),
        age=data.get('age'),
        gender=data.get('gender'),
        illness_type=data.get('illness_type'),
        hospital_name=data.get('hospital_name'),
        hospital_location=data.get('hospital_location'),
        estimated_cost=data.get('estimated_cost'),
        urgency=data.get('urgency'),
        description=data.get('description'),
        status='submitted'
    )
    db.session.add(case)
    db.session.commit()
    return jsonify({'success': True, 'case_id': case.id})

@app.route('/new-case')
@login_required
def new_case():
    user = User.query.get(session['user_id'])
    return render_template('emergency_case.html', user=user, illness_types=ILLNESS_TYPES)

@app.route('/case/<case_id>')
@login_required
def case_detail(case_id):
    case = Case.query.get(case_id)
    if not case:
        return render_template('404.html'), 404
    if case.user_id != session['user_id'] and session.get('user_type') not in ['hospital', 'funder', 'admin']:
        return render_template('unauthorized.html'), 403
    
    user = User.query.get(session['user_id'])
    documents = Document.query.filter_by(case_id=case_id).all()
    applications = Application.query.filter_by(case_id=case_id).all()
    payment = Payment.query.filter_by(case_id=case_id).first()
    
    return render_template('case_detail.html', 
                         case=case, 
                         user=user,
                         documents=documents,
                         applications=applications,
                         payment=payment,
                         document_types=DOCUMENT_TYPES)

@app.route('/upload-document', methods=['POST'])
@login_required
def upload_document():
    case_id = request.form.get('case_id')
    doc_type = request.form.get('doc_type')
    file = request.files.get('file')
    
    case = Case.query.get(case_id)
    if not case or case.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if not file:
        return jsonify({'success': False, 'message': 'No file provided'})
    
    filename = secure_filename(f"{case_id}_{doc_type}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    doc = Document(
        id=str(uuid.uuid4()),
        case_id=case_id,
        user_id=session['user_id'],
        doc_type=doc_type,
        file_name=file.filename,
        file_path=filepath,
        file_size=os.path.getsize(filepath)
    )
    db.session.add(doc)
    
    # Update case status to documents_pending if this is first upload
    if case.status == 'submitted':
        case.status = 'documents_pending'
    
    db.session.commit()
    return jsonify({'success': True, 'document_id': doc.id})

@app.route('/download-document/<doc_id>')
@login_required
def download_document(doc_id):
    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'success': False, 'message': 'Document not found'}), 404
    
    # Check authorization
    case = Case.query.get(doc.case_id)
    is_owner = case.user_id == session['user_id']
    is_hospital = session.get('user_type') == 'hospital'
    is_funder = session.get('user_type') == 'funder'
    is_admin = session.get('user_type') == 'admin'
    
    if not (is_owner or is_hospital or is_funder or is_admin):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if os.path.exists(doc.file_path):
        return send_file(doc.file_path, as_attachment=True, download_name=doc.file_name)
    return jsonify({'success': False, 'message': 'File not found'}), 404

@app.route('/funding-options/<case_id>')
@login_required
def funding_options(case_id):
    case = Case.query.get(case_id)
    if not case:
        return render_template('404.html'), 404
    if case.user_id != session['user_id']:
        return render_template('unauthorized.html'), 403
    
    user = User.query.get(session['user_id'])
    
    # Get matched funders
    matched_funders = match_funding_sources(case.to_dict())
    
    # Get existing applications
    existing_apps = Application.query.filter_by(case_id=case_id).all()
    app_org_ids = [a.org_id for a in existing_apps]
    
    return render_template('funding_options.html',
                         case=case,
                         user=user,
                         matched_funders=matched_funders,
                         existing_apps=existing_apps,
                         app_org_ids=app_org_ids)

@app.route('/apply-funding', methods=['POST'])
@login_required
def apply_funding():
    data = request.get_json()
    case_id = data.get('case_id')
    org_id = data.get('org_id')
    org_name = data.get('org_name')
    
    case = Case.query.get(case_id)
    if not case or case.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Check if already applied
    existing = Application.query.filter_by(case_id=case_id, org_id=org_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already applied to this funder'})
    
    # Check if documents verified
    docs = Document.query.filter_by(case_id=case_id).all()
    if not docs:
        return jsonify({'success': False, 'message': 'Please upload documents first'})
    
    all_verified = all(d.verified for d in docs)
    if not all_verified:
        return jsonify({'success': False, 'message': 'Not all documents are verified yet'})
    
    app = Application(
        id=str(uuid.uuid4()),
        case_id=case_id,
        user_id=session['user_id'],
        org_id=org_id,
        org_name=org_name,
        status='submitted'
    )
    db.session.add(app)
    
    # Update case status
    if case.status == 'documents_pending':
        case.status = 'verified'
    
    db.session.commit()
    return jsonify({'success': True, 'application_id': app.id})

@app.route('/track-status/<case_id>')
@login_required
def track_status(case_id):
    case = Case.query.get(case_id)
    if not case:
        return render_template('404.html'), 404
    if case.user_id != session['user_id']:
        return render_template('unauthorized.html'), 403
    
    user = User.query.get(session['user_id'])
    documents = Document.query.filter_by(case_id=case_id).all()
    applications = Application.query.filter_by(case_id=case_id).all()
    payment = Payment.query.filter_by(case_id=case_id).first()
    
    return render_template('track_status.html',
                         case=case,
                         user=user,
                         documents=documents,
                         applications=applications,
                         payment=payment)

@app.route('/my-funding')
@login_required
def my_funding():
    user = User.query.get(session['user_id'])
    user_cases = Case.query.filter_by(user_id=session['user_id']).all()
    payments = Payment.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('my_funding.html',
                         user=user,
                         user_cases=user_cases,
                         payments=payments)


# ============================================================
#  ROUTES — HOSPITAL STAFF
# ============================================================

@app.route('/hospital-dashboard')
@role_required('hospital')
def hospital_dashboard():
    user = User.query.get(session['user_id'])
    
    # Cases with documents pending verification
    cases_pending = Case.query.filter_by(status='documents_pending').all()
    
    # Cases already verified by this hospital
    cases_verified = Case.query.filter_by(verified_by=session['user_id']).all()
    
    return render_template('hospital_dashboard.html',
                         user=user,
                         cases_pending=cases_pending,
                         cases_verified=cases_verified)

@app.route('/hospital/verify-documents', methods=['POST'])
@role_required('hospital')
def hospital_verify_documents():
    data = request.get_json()
    case_id = data.get('case_id')
    doc_id = data.get('doc_id')
    action = data.get('action')  # 'approve' or 'reject'
    reason = data.get('reason', '')
    
    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'success': False, 'message': 'Document not found'})
    
    if action == 'approve':
        doc.verified = True
        doc.verified_by = session['user_id']
        doc.verified_at = datetime.utcnow()
    else:
        doc.verified = False
        doc.rejection_reason = reason
    
    db.session.commit()
    
    # Check if all documents are verified
    case = Case.query.get(case_id)
    all_docs = Document.query.filter_by(case_id=case_id).all()
    all_verified = all(d.verified for d in all_docs) if all_docs else False
    
    if all_verified:
        case.status = 'verified'
        case.verified_by = session['user_id']
        case.verified_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify({'success': True, 'all_verified': all_verified})

@app.route('/hospital/case/<case_id>')
@role_required('hospital')
def hospital_case_detail(case_id):
    case = Case.query.get(case_id)
    if not case:
        return render_template('404.html'), 404
    
    user = User.query.get(session['user_id'])
    documents = Document.query.filter_by(case_id=case_id).all()
    patient_user = User.query.get(case.user_id)
    
    return render_template('hospital_case_detail.html',
                         case=case,
                         user=user,
                         patient_user=patient_user,
                         documents=documents)


# ============================================================
#  ROUTES — FUNDER (NGO / CSR / INSURANCE)
# ============================================================

@app.route('/funder-dashboard')
@role_required('funder')
def funder_dashboard():
    user = User.query.get(session['user_id'])
    
    # Get all verified cases with pending applications
    verified_cases = Case.query.filter_by(status='verified').all()
    pending_applications = Application.query.filter_by(status='submitted').all()
    
    return render_template('funder_dashboard.html',
                         user=user,
                         verified_cases=verified_cases,
                         pending_applications=pending_applications)

@app.route('/funder/review-application/<app_id>')
@role_required('funder')
def funder_review_application(app_id):
    application = Application.query.get(app_id)
    if not application:
        return render_template('404.html'), 404
    
    case = Case.query.get(application.case_id)
    patient_user = User.query.get(case.user_id)
    documents = Document.query.filter_by(case_id=case.id).all()
    user = User.query.get(session['user_id'])
    
    return render_template('funder_review_application.html',
                         application=application,
                         case=case,
                         patient_user=patient_user,
                         documents=documents,
                         user=user)

@app.route('/funder/respond', methods=['POST'])
@role_required('funder')
def funder_respond():
    data = request.get_json()
    app_id = data.get('application_id')
    action = data.get('action')  # 'approve' or 'reject'
    note = data.get('note', '')
    amount = data.get('amount', 0)
    
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'})
    
    application.status = 'approved' if action == 'approve' else 'rejected'
    application.note = note
    application.updated_at = datetime.utcnow()
    
    if action == 'approve':
        application.amount_offered = int(amount)
        
        # Create payment record
        case = Case.query.get(application.case_id)
        patient_user = User.query.get(case.user_id)
        
        payment = Payment(
            id=str(uuid.uuid4()),
            case_id=case.id,
            user_id=case.user_id,
            total_amount=int(amount),
            status='processing',
            bank_name=patient_user.bank_name,
            account_number=patient_user.account_number,
            ifsc_code=patient_user.ifsc_code,
            account_holder=patient_user.account_holder,
            transaction_id=f"TXN{str(uuid.uuid4())[:12].upper()}",
            reference_id=f"REF{case.id[:8]}"
        )
        db.session.add(payment)
        
        case.status = 'approved_for_funding'
        case.approved_by = session['user_id']
        case.approved_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'new_status': application.status})


# ============================================================
#  ROUTES — ADMIN
# ============================================================

@app.route('/admin-dashboard')
@role_required('admin')
def admin_dashboard():
    user = User.query.get(session['user_id'])
    all_users = User.query.order_by(User.created_at.desc()).all()
    all_cases = Case.query.order_by(Case.created_at.desc()).all()
    all_payments = Payment.query.all()
    
    stats = {
        'total_users': len(all_users),
        'families': sum(1 for u in all_users if u.user_type == 'family'),
        'hospitals': sum(1 for u in all_users if u.user_type == 'hospital'),
        'funders': sum(1 for u in all_users if u.user_type == 'funder'),
        'total_cases': len(all_cases),
        'submitted': sum(1 for c in all_cases if c.status == 'submitted'),
        'documents_pending': sum(1 for c in all_cases if c.status == 'documents_pending'),
        'verified': sum(1 for c in all_cases if c.status == 'verified'),
        'approved_for_funding': sum(1 for c in all_cases if c.status == 'approved_for_funding'),
        'funded': sum(1 for c in all_cases if c.status == 'funded'),
        'total_payments': len(all_payments),
        'pending_payments': sum(1 for p in all_payments if p.status == 'pending'),
        'released_payments': sum(1 for p in all_payments if p.status == 'completed'),
        'total_funded': sum(p.released_amount for p in all_payments if p.status == 'completed')
    }
    
    return render_template('admin_dashboard.html',
                         user=user,
                         all_users=all_users,
                         all_cases=all_cases,
                         all_payments=all_payments,
                         stats=stats)

@app.route('/admin/release-payment/<payment_id>', methods=['POST'])
@role_required('admin')
def admin_release_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'success': False, 'message': 'Payment not found'})
    
    payment.status = 'completed'
    payment.released_at = datetime.utcnow()
    payment.released_amount = payment.total_amount
    
    # Update case status
    case = Case.query.get(payment.case_id)
    if case:
        case.status = 'funded'
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Payment released successfully'})

@app.route('/admin/delete-case/<case_id>', methods=['POST'])
@role_required('admin')
def admin_delete_case(case_id):
    case = Case.query.get(case_id)
    if case:
        Payment.query.filter_by(case_id=case_id).delete()
        Application.query.filter_by(case_id=case_id).delete()
        Document.query.filter_by(case_id=case_id).delete()
        db.session.delete(case)
        db.session.commit()
    return jsonify({'success': True})


# ============================================================
#  API
# ============================================================

@app.route('/api/user')
def api_user():
    if 'user_id' not in session:
        return jsonify({'logged_in': False})
    user = User.query.get(session['user_id'])
    return jsonify({
        'logged_in': True,
        'user': user.to_dict() if user else {},
        'user_type': session.get('user_type')
    })

@app.route('/api/case/<case_id>')
def api_case(case_id):
    case = Case.query.get(case_id)
    if not case:
        return jsonify({'error': 'Case not found'}), 404
    return jsonify(case.to_dict())

@app.route('/api/case/<case_id>/documents')
def api_case_documents(case_id):
    documents = Document.query.filter_by(case_id=case_id).all()
    return jsonify([d.to_dict() for d in documents])

@app.route('/api/case/<case_id>/applications')
def api_case_applications(case_id):
    applications = Application.query.filter_by(case_id=case_id).all()
    return jsonify([a.to_dict() for a in applications])


# ============================================================
#  ERROR PAGES
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ============================================================
#  STARTUP
# ============================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables ready.")
    app.run(debug=True, port=5000)
