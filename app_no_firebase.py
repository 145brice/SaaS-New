"""
Flask web application - Dashboard and API (No Firebase)
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'
CORS(app)

# Mock data for testing
MOCK_LEADS = [
    {
        'county': 'Nashville-Davidson',
        'permit_number': 'BP-2025-001234',
        'address': '123 Broadway, Nashville, TN 37203',
        'permit_type': 'New Construction - Commercial',
        'estimated_value': 250000,
        'work_description': 'New office building construction',
        'score': 85
    },
    {
        'county': 'Rutherford',
        'permit_number': 'BP-2025-005678',
        'address': '456 Main St, Murfreesboro, TN 37130',
        'permit_type': 'Renovation - Residential',
        'estimated_value': 150000,
        'work_description': 'Major home renovation',
        'score': 78
    }
]

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Landing page"""
    return '''
    <html>
        <head>
            <title>Contractor Leads SaaS</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .hero { background: #f5f5f5; padding: 40px; border-radius: 8px; margin: 20px 0; }
                .cta { background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
                .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 40px 0; }
                .feature { background: white; border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>🏗️ Contractor Leads SaaS</h1>
            <div class="hero">
                <h2>Get High-Quality Construction Leads Daily</h2>
                <p>We scrape building permits from multiple counties and deliver qualified leads directly to your inbox.</p>
                <a href="/dashboard" class="cta">View Dashboard</a>
                <a href="/login" style="margin-left: 10px;" class="cta">Login</a>
            </div>
            <div class="features">
                <div class="feature">
                    <h3>�� AI-Scored Leads</h3>
                    <p>Our AI ranks leads by value and relevance</p>
                </div>
                <div class="feature">
                    <h3>📧 Daily Delivery</h3>
                    <p>Fresh leads in your inbox every morning</p>
                </div>
                <div class="feature">
                    <h3>🗺️ Multi-County</h3>
                    <p>Coverage across Nashville, Rutherford, Wilson & more</p>
                </div>
            </div>
        </body>
    </html>
    '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        session['email'] = email
        session['user_id'] = 'demo-user'
        return redirect(url_for('dashboard'))
    
    return '''
    <html>
        <head>
            <title>Login - Contractor Leads</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
                input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
                button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <h2>Login</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p><a href="/">Back to Home</a></p>
        </body>
    </html>
    '''


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - shows daily leads"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    return f'''
    <html>
        <head>
            <title>Dashboard - Contractor Leads</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; }}
                .lead {{ background: white; border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }}
                .score {{ background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; }}
                .value {{ color: #007bff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Dashboard</h1>
                <div>
                    <span>Welcome, {session.get('email')}</span> | 
                    <a href="/logout">Logout</a>
                </div>
            </div>
            <h2>Today's Leads ({date_str})</h2>
            <p>Found {len(MOCK_LEADS)} leads today</p>
            
            {''.join([f'''
            <div class="lead">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <h3>{lead['address']}</h3>
                        <p><strong>County:</strong> {lead['county']}</p>
                        <p><strong>Permit #:</strong> {lead['permit_number']}</p>
                        <p><strong>Type:</strong> {lead['permit_type']}</p>
                        <p><strong>Description:</strong> {lead['work_description']}</p>
                        <p class="value">Estimated Value: ${lead['estimated_value']:,}</p>
                    </div>
                    <div>
                        <span class="score">Score: {lead['score']}/100</span>
                    </div>
                </div>
            </div>
            ''' for lead in MOCK_LEADS])}
        </body>
    </html>
    '''


@app.route('/api/leads')
def api_leads():
    """API endpoint to download CSV leads by city"""
    import glob
    from flask import send_file
    
    city = request.args.get('city', '').lower()
    stripe_customer_id = request.args.get('customer_id', '')
    
    if not city:
        return jsonify({'error': 'City parameter required'}), 400
    
    # Test emails that bypass Stripe validation
    test_emails = ['145brice@gmail.com', 'test@example.com']
    
    # For production, validate Stripe customer
    # if stripe_customer_id not in test_emails:
    #     # Validate with Stripe here
    #     pass
    
    # Option 1: Leads stored in same backend directory (for Render deployment)
    # leads_base = os.path.join(os.path.dirname(__file__), 'leads', city)
    
    # Option 2: Leads stored in frontend directory (for local development)
    frontend_leads = os.path.join(os.path.dirname(__file__), '..', '..', 'Fresh Repo Permits Clone', 'Permits-Front-End', 'leads', city)
    backend_leads = os.path.join(os.path.dirname(__file__), 'leads', city)
    
    # Try backend first (production), then frontend (local dev)
    if os.path.exists(backend_leads):
        leads_base = backend_leads
    elif os.path.exists(frontend_leads):
        leads_base = frontend_leads
    else:
        return jsonify({'error': f'No leads directory found for {city}'}), 404
    
    # Find the most recent date folder
    try:
        date_folders = sorted([d for d in os.listdir(leads_base) if os.path.isdir(os.path.join(leads_base, d))], reverse=True)
    except Exception as e:
        return jsonify({'error': f'Error reading leads directory: {str(e)}'}), 500
    
    if not date_folders:
        return jsonify({'error': f'No date folders found for {city}'}), 404
    
    latest_date = date_folders[0]
    csv_pattern = os.path.join(leads_base, latest_date, f'*{city}*.csv')
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        return jsonify({'error': f'No CSV files found for {city}'}), 404
    
    csv_file = csv_files[0]
    filename = os.path.basename(csv_file)
    
    return send_file(
        csv_file,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    print(f"\n🚀 Starting Contractor Leads on http://localhost:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=True)
