from flask import Flask, render_template, request, url_for, redirect, session, after_this_request
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv(override=True)
from database import email_inserter, vote_inserter, data_fetcher
from security import hash_email

# App Configuration

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2)
app.config['SESSION_REFRESH_EACH_REQUEST'] = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_for=1)


# Google Authentication

blueprint = make_google_blueprint(
    client_id = os.getenv('OAUTH_CLIENT_ID'), 
    client_secret = os.getenv('OAUTH_CLIENT_SECRET'), 
    scope=['openid', 'https://www.googleapis.com/auth/userinfo.email'],
    redirect_to='sign_in', 
    reprompt_select_account=True,
    hosted_domain= (f'{os.getenv('FLASK_HOSTED_DOMAIN')}')
    )

app.register_blueprint(blueprint, url_prefix='/login')

# App Routes

@app.route('/', methods=['POST', 'GET'])
def index ():
    session.clear()
    return render_template('welcome.html')

@app.route('/legal', methods=['POST', 'GET'])
def legal ():
    session.clear()
    return render_template('legal.html')

@app.route('/signin', methods=['POST', 'GET'])
def sign_in(): 
    session.permanent = True

    if not google.authorized:
        return redirect(url_for('google.login'))
    
    # Verifying Google OAuth
    resp = google.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text
    info = resp.json()

    # Storing Email Hash in Browser Cookies
    session['user_email_hash'] = hash_email(info['email'])

    if email_inserter(session['user_email_hash']):
        session.clear()
        return redirect(url_for('error'))
    else:
        return redirect(url_for('get_voter_data'))

@app.route('/vote', methods=['GET', 'POST'])
def get_voter_data():

    # Session Token Check & Passing variables for Jinja2

    if google.authorized:
        return render_template('vote.html', student_data = data_fetcher())
    else:
        return redirect(url_for('error'))
    
@app.route('/submit', methods=['POST', 'GET'])
def submit_vote():

    # Receiving Form Data w/ session token & DB double vote check

    if request.method == 'POST' and google.authorized:
        if not vote_inserter(session.get('user_email_hash'), request.form):
            return redirect(url_for('error'))
        return redirect(url_for('thank_user'))
    else:
        return redirect(url_for('error'))
    
@app.route('/thanks')
def thank_user():
    session.clear()
    return render_template('thank_you.html')

@app.route('/error')
def error():
    session.clear()
    return render_template('error.html')

# Delete all browser cache after closing
    
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Flask Development Server Config
        
if __name__ == '__main__':
    app.run(debug=True, port=5000)

