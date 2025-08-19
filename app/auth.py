from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models.database import User, db

auth_bp = Blueprint('auth', __name__)

# Hard-coded users for MVP
DEMO_USERS = {
    'admin': {
        'username': 'admin',
        'email': 'admin@pikacanvas.com',
        'password_hash': generate_password_hash('admin123'),
        'id': 1
    },
    'demo': {
        'username': 'demo',
        'email': 'demo@pikacanvas.com', 
        'password_hash': generate_password_hash('demo123'),
        'id': 2
    }
}

def init_demo_users():
    """Initialize demo users in database if they don't exist"""
    for username, user_data in DEMO_USERS.items():
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
            db.session.add(user)
    db.session.commit()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check against demo users
        if username in DEMO_USERS:
            user_data = DEMO_USERS[username]
            if check_password_hash(user_data['password_hash'], password):
                # Get or create user in database
                user = User.query.filter_by(username=username).first()
                if not user:
                    init_demo_users()
                    user = User.query.filter_by(username=username).first()
                
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
            else:
                flash('Invalid username or password')
        else:
            flash('Invalid username or password')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))