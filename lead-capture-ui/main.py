from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# User model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)

# Mock database (replace with a real database in production)
users = {
    1: User(1, 'admin', os.getenv('ADMIN_PASSWORD', 'admin123')),
    2: User(2, 'Steve', os.getenv('ADMIN_PASSWORD', 'admin123')),
    3: User(3, 'Bugs', os.getenv('ADMIN_PASSWORD', 'admin123')),
    4: User(4, 'Ricki', os.getenv('ADMIN_PASSWORD', 'admin123'))
}

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = next((u for u in users.values() if u.username == username), None)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/analyze-email', methods=['POST'])
@login_required
def analyze_email():
    
### FOR DEBUG
#     return {
#   "company_domain": "company.com",
#   "linkedin_profile": "https://www.linkedin.com/company/company/",
#   "cheat_sheet_bullets": "Company is a global leader in sustainable climate solutions across heating, cooling, and renewable energy systems., With over 100 years of innovation, Company invests heavily in R&D to optimize product performance and efficiency., Quix can streamline data capture and analysis across Company's testing facilities for boilers, heat pumps, and solar systems., By leveraging Quix's real-time processing, Company can accelerate product iteration cycles and time-to-market., Quix's Python-friendly platform empowers Company's engineers to develop custom data processing without infrastructure overhead., Integrating Quix can drive operational efficiencies and cost savings across Company's global network of 22 production companies."
# }
    
    
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Prepare the prompt for Claude
        # Using a raw string to handle special characters in the prompt
        prompt = f"""Analyze this email address and provide relevant information:
        Email: {email}

        # AI Research Prompt for Quix Sales Team
        
        You are a business intelligence assistant helping create sales cheat sheets for Quix, a data management platform company. When given a company name, follow these steps:

        ## Step 1: Company Research
        Search for and analyze the target company to identify:
        - **Core business description**: What does the company do? What industry are they in?
        - **R&D and testing facilities**: Look specifically for mentions of:
        - Wind tunnels
        - Engine dynos
        - Climatic test chambers
        - Human-in-the-loop simulators
        - Materials testing labs
        - Vibration test equipment
        - Acoustic chambers
        - Thermal testing facilities
        - Any other specialized testing rigs or R&D equipment

        ## Step 2: Strategic Intelligence
        Find and review:
        - Most recent annual report or shareholder letter
        - Company goals, strategic initiatives, and future aspirations
        - Recent press releases about R&D investments or new testing capabilities
        - Any mentions of data challenges, digital transformation initiatives, or testing efficiency improvements

        ## Step 3: Quix Value Proposition Context
        Consider how Quix can help this company:
        - **Quix offers**: A data management platform for companies with testing and R&D facilities
        - **Key benefits**: Capture, process, and understand test rig data more effectively than in-house solutions
        - **Cost advantage**: Cheaper than building custom solutions regardless of company size
        - **Ease of use**: Software developers and R&D engineers can develop Python scripts to process test data without needing infrastructure deployment knowledge
        - **Real-time capabilities**: Scalable, real-time data processing infrastructure

        ## Step 4: Generate Sales Cheat Sheet
        Create 5-7 concise bullet points that:
        - Demonstrate understanding of the company's business and testing operations
        - Connect their goals/challenges to Quix's capabilities
        - Use specific language that shows you understand their industry
        - Focus on outcomes and benefits rather than technical features
        - Include references to their stated goals or recent initiatives when possible
        - Ensure the customer goals or outcomes are listed first then how Quix can help e.g. Goal: Customer wants to XXX. Quix can YYY. 
        
        ## Required JSON Output Format

        Output JSON with the following fields, ONLY output the JSON object, nothing else. 
                
        company_domain
        linkedin_profile
        cheat_sheet_bullets
    
        DO NOT add anything else like 'Here is the requested analysis in JSON format:'
        
        **Important Notes:**
        - The cheat_sheet_bullets field should be a single CSV string with each bullet point separated by pipes e.g. |
        - Each bullet point should be 10-25 words and action-oriented
        - Focus on business outcomes, not technical specifications
        - If no R&D/testing facilities are found, note this and focus on potential data processing needs in their industry
        - Always verify URLs are accurate and current

        ## Step 0: Email Domain Analysis
        When provided with an email address:
        - Extract the domain name from the email (e.g., from "john.doe@boeing.com" extract "boeing.com")
        - Use the domain to identify the company name and primary website
        - Note: Some emails may use subsidiary domains or regional variations - research accordingly
        - If the domain doesn't clearly indicate the company (e.g., gmail.com), inform that company identification is not possible

        **Example Usage:**
        Input: "Research john.smith@boeing.com for Quix sales approach"
        Process: Extract "boeing.com" → Identify as Boeing Company → Research aerospace testing facilities
        Output: JSON with domain, LinkedIn, and tailored bullet points about their aerospace testing facilities and how Quix supports their R&D data challenges.

        """
        
        # Call Claude API
        headers = {
            'x-api-key': app.config['ANTHROPIC_API_KEY'],
            'content-type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': 'claude-3-opus-20240229',
            'max_tokens': 1000,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            error_details = response.json() if response.content else 'No error details available'
            print(f"API Error: {response.status_code}", error_details)
            return jsonify({
                'error': 'Failed to analyze email',
                'status_code': response.status_code,
                'details': error_details
            }), 500
        
        result = response.json()
        print("API Response:", result)  # Debug log
        
        # Safely extract the content
        try:
            analysis_text = result.get('content', [{}])[0].get('text', '')
            if not analysis_text:
                raise ValueError('No analysis text in response')
                
            # Parse the JSON string in analysis_text
            try:
                parsed_data = json.loads(analysis_text)
                
                # Add username to the data
                parsed_data['email'] = email
                parsed_data['requested_by'] = current_user.username
                
                # Send data to webhook endpoint if configured
                webhook_url = os.getenv('ANALYSIS_WEBHOOK_URL')
                if webhook_url:
                    try:
                        requests.post(
                            webhook_url,
                            json=parsed_data,
                            timeout=5  # 5 second timeout
                        )
                    except Exception as webhook_error:
                        print(f"Error sending data to webhook: {webhook_error}")
                
                return jsonify(parsed_data)
                
            except json.JSONDecodeError as e:
                print("Error parsing JSON from Claude response:", e)
                raise ValueError('Invalid JSON format in response')
        except (KeyError, IndexError, AttributeError) as e:
            print("Error parsing API response:", e)
            return jsonify({
                'error': 'Error parsing API response',
                'details': str(e),
                'raw_response': result
            }), 500
        
    except Exception as e:
        print(e)
        return jsonify({
            'error': 'An error occurred',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=80)
