# Fix Guide - TemplateNotFound Error

## Problem
Error: `jinja2.exceptions.TemplateNotFound: index.html`

This happens because required HTML templates are missing from your templates/ folder.

## Solution - Copy These Files to templates/ Folder

### Step 1: Ensure templates folder exists
```bash
mkdir -p templates
```

### Step 2: Copy ALL these files to templates/

NEW files from delivery package:
- index.html
- profile.html
- case_detail.html
- hospital_case_detail.html
- funder_review_application.html
- track_status.html
- my_funding.html

ORIGINAL files you may already have:
- base.html (if missing, create it - see below)
- login.html
- register.html
- dashboard.html
- emergency_case.html
- funding_options.html
- hospital_dashboard.html
- funder_dashboard.html
- admin_dashboard.html
- nearby_support.html
- 404.html
- 500.html
- unauthorized.html

## Step 3: Create Missing base.html

If you don't have base.html, create templates/base.html with this content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CareFor Now{% endblock %}</title>
    <style>
        :root {
            --primary: #2c5aa0;
            --primary-dark: #1a3a5c;
            --accent: #e74c3c;
            --text-primary: #2c3e50;
            --text-muted: #7f8c8d;
            --bg: #f8f9fa;
            --border: #e0e0e0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: var(--text-primary);
            background: white;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .container-md {
            max-width: 600px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .card {
            background: white;
            border: 0.5px solid var(--border);
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .card-header {
            padding: 20px;
            border-bottom: 0.5px solid var(--border);
            background: var(--bg);
        }
        
        .card-body {
            padding: 20px;
        }
        
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-weight: 600;
        }
        
        .btn:hover {
            background: var(--primary-dark);
        }
        
        .alert {
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        
        .alert-success { background: #d4edda; color: #155724; }
        .alert-danger { background: #f8d7da; color: #721c24; }
        .alert-info { background: #d1ecf1; color: #0c5460; }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border);
            border-radius: 4px;
        }
        
        .form-control:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        header {
            background: white;
            border-bottom: 1px solid var(--border);
            padding: 15px 0;
        }
        
        header a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }
        
        footer {
            background: var(--bg);
            padding: 20px 0;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--text-muted);
            font-size: 14px;
        }
    </style>
</head>
<body>
    <header>
        <div class="container" style="display: flex; justify-content: space-between; align-items: center; padding: 15px 0;">
            <div>
                <a href="/" style="font-size: 20px; font-weight: 800;">💙 CareFor Now</a>
            </div>
            <nav style="display: flex; gap: 20px;">
                {% if session.get('user_id') %}
                    <a href="/dashboard">Dashboard</a>
                    <a href="/logout">Logout</a>
                {% else %}
                    <a href="/login">Login</a>
                    <a href="/register">Register</a>
                {% endif %}
            </nav>
        </div>
    </header>
    
    <main style="min-height: calc(100vh - 200px);">
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; 2024 CareFor Now</p>
        </div>
    </footer>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

## Step 4: Quick Stub Templates

If you don't have other templates, create basic stubs. For example, create templates/login.html:

```html
{% extends "base.html" %}
{% block content %}
<div class="container-md" style="padding: 40px 0;">
    <h1>Login</h1>
    <form method="POST" style="margin-top: 20px;">
        <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" required>
        </div>
        <button class="btn">Login</button>
    </form>
</div>
{% endblock %}
```

Do the same for: register.html, dashboard.html, etc.

## Complete File List

Your templates folder should have (minimum):

```
templates/
├── base.html (REQUIRED - create if missing)
├── index.html (from delivery package)
├── login.html
├── register.html
├── dashboard.html
├── profile.html (from delivery package)
├── emergency_case.html
├── case_detail.html (from delivery package)
├── hospital_case_detail.html (from delivery package)
├── hospital_dashboard.html
├── funder_dashboard.html
├── funder_review_application.html (from delivery package)
├── admin_dashboard.html
├── funding_options.html
├── track_status.html (from delivery package)
├── my_funding.html (from delivery package)
├── nearby_support.html
├── 404.html
├── 500.html
└── unauthorized.html
```

## After Adding Templates

1. Restart Flask server
2. Clear Python cache: Delete __pycache__ folder
3. Try again: python app.py
4. Open http://localhost:5000

The app should now work!

## Need the Missing Templates?

All the NEW templates are in the delivery package:
- index.html
- profile.html
- case_detail.html
- hospital_case_detail.html
- funder_review_application.html
- track_status.html
- my_funding.html

For the ORIGINAL templates from your existing project, check if you still have them backed up, or create stub versions as shown above.

## Troubleshooting

Error: Still getting TemplateNotFound
→ Check templates folder exists: ls -la templates/
→ Check file names match exactly
→ Make sure you're in the right directory
→ Restart Flask: Stop Ctrl+C and run python app.py again

Error: base.html not found
→ base.html is referenced by all other templates
→ Create it in templates/ folder (code above)
→ It's the main layout template

Everything working now?
→ Great! Continue with QUICK_START.md
