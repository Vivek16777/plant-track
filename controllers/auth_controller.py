from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from database.connection import db

class AuthController:
    @staticmethod
    def register():
        """Handle new user registration"""
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'Farmer')
            
            # Check duplicates
            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'danger')
                return render_template('auth/register.html')
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'danger')
                return render_template('auth/register.html')
                
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving user: {e}', 'danger')
                
        return render_template('auth/register.html')

    @staticmethod
    def login():
        """Handle user login and authentication session"""
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                flash('Invalid username or password.', 'danger')
                return render_template('auth/login.html')
                
            login_user(user, remember=remember)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
            
        return render_template('auth/login.html')

    @staticmethod
    def logout():
        """Terminate authentication session and redirect"""
        logout_user()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('auth.login'))
