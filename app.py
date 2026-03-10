import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template, redirect, url_for
from config import Config
from models import init_db, migrate_db
from utils.email_service import init_mail
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.owner import owner_bp
from routes.customer import customer_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE

# Initialize configuration
Config.init_app()

# Initialize mail service
init_mail(app)

# Initialize database
init_db()

# Run migrations
migrate_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(owner_bp)
app.register_blueprint(customer_bp)

@app.route('/')
def index():
    """Home page - redirect to login"""
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
