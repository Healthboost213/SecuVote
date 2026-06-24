# SecuVote - Documentation

### Notice:
SecuVote is a platform agnostic utility but you would have a better experience running it on Linux. I have personally tested it on Ubuntu Server 26.04 and Red Hat Enterprise Linux and had a straightforward experience setting it up. I've tried my level best to make the code as modularized as possible so things can be replaced at will. 

### Prerequisites (Tested on Ubuntu Server 26.04):

- Python 3.12+
- MySQL Server 8.4+
- Gunicorn (w/ Python venv setup and activated)
- Access to Google Cloud Console w/ correct roles
- Domain with SSL Certificate (or Tailscale)
- Nginx (for reverse proxying)

The app would really benefit from having a faster processor. Anything from the past decade should suffice. I tested it on a system with i5-4200U and 8GB of RAM and it was functional.

### Cloning the Repository:

```
git clone https://github.com/Healthboost213/SecuVote.git
```
Clone it somewhere convenient and provide necessary execution permissions in Linux.

### Google OAuth Consent Set-up

Google OAuth requires you to select whether it is an internal or external tool. It's better to set it as internal for testing and moving to external when ready to publish. OAuth requires all traffic routed over HTTPS protocol. A simple way of accessing this is by pointing the authorized redirect URIs to a Tailscale Funnel. 

Otherwise, If using externally, a domain with a valid SSL certificate is required. Google mandates for a ToS and privacy policy page. Depending on the scopes selected, Google can verify your website within 48 hours. This application only requires the Email and OpenID scopes from Google to function properly.

### Environment (.env) File Setup
An environment file is required for easier set-up of the application. This allows changes in configuration to be more easier to update.

```
OAUTH_CLIENT_ID=
OAUTH_CLIENT_SECRET=
DATABASE_IP=
DATABASE_USER=
DATABASE_PASSWORD=
FLASK_SECRET_KEY=
EMAIL_HASH_SALT=

# Be very careful not to share this file with others. 
# Ensure proper access rights are set in Linux. 
# For Flask Secret Key and Email Hash, use python module 'secrets' to generate a random string.
```

### Basic Deployment of SecuVote:

After cloning the repository and setting up venv, install the necessary dependencies by running:
```
pip install -r requirements.txt
pip install gunicorn
```
Assuming MySQL is set-up with user permissions correctly configured:
```
mysql -u [username] -p [database name] < 'schema.sql'
```

You can deploy the Flask app by running:
```
gunicorn -w [worker count] app:app
```

### Additional Configuration
For larger use cases involving 250+ people, it is recommended to use Nginx to serve static files. For this configuration, Gunicorn must be set as a reverse proxy in the Nginx configuration. Additional options can be set-up such a g-zip compression or rate-limiting for additional speed and security.

```
# Reverse Proxy

location / {
            
    proxy_pass "http://127.0.0.1:8000";

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;

}

# Static File Serve

location /static/ {

    alias [ADD PATH FROM ROOT DIR TO APP FOLDER HERE];
    expires 3d;

}

```

### Regarding HTTPS Requirements
Google OAuth absolutely requires HTTPS because secrets and tokens are sent back and forth which attackers can use to perform session hijacking or MITM attacks. It is highly recommended even while running a small instance to set-up SSL + TLS certificates.

For testing, I would recommend Tailscale or similar alternatives. Tailscale provides the necessary HTTPS certificates and encrypts all data in transit through HTTPS. It is very easy to set-up and would also make remote access to systems far more easier.

If you are running the app under your own domain, ensure you are registered and have valid certificates. A proper domain is required if the application is needed to be accessed over the internet freely. An audit is performed by Google on your website to ensure everything is correct. 