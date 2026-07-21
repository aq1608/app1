from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from config import Config
from models import db, User, Therapist, UserTherapistMatch, DailyCheckIn, ForumPost, DailyTask, UserTaskCompletion
from forms import LoginForm, RegistrationForm, QuestionnaireForm
from datetime import date

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mail = Mail(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize Admin
    admin = Admin(app, name='SUICINO Admin', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Therapist, db.session))
    admin.add_view(ModelView(UserTherapistMatch, db.session))
    
    # Routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))  # Changed from 'dashboard' to 'home'
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home'))  # Changed from 'dashboard' to 'home'
            flash('Invalid username or password', 'error')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if user already exists
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already exists', 'error')
                return render_template('register.html', form=form)
            
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already registered', 'error')
                return render_template('register.html', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                birthday=form.birthday.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('questionnaire'))
        
        return render_template('register.html', form=form)
    
    @app.route('/questionnaire', methods=['GET', 'POST'])
    @login_required
    def questionnaire():
        if current_user.questionnaire_completed:
            return redirect(url_for('home'))
        
        form = QuestionnaireForm()
        if form.validate_on_submit():
            current_user.mental_illness = form.mental_illness.data
            current_user.preferred_therapist_gender = form.preferred_therapist_gender.data
            current_user.preferred_language = form.preferred_language.data
            current_user.questionnaire_completed = True
            
            db.session.commit()
            flash('Questionnaire completed!', 'success')
            return redirect(url_for('home'))
        
        return render_template('questionnaire.html', form=form)
    
    # Add these routes to your existing app.py

    @app.route('/home')
    @login_required
    def home():
        # Daily check-in page
        today_checkin = DailyCheckIn.query.filter_by(
            user_id=current_user.id, 
            date=date.today()
        ).first()
        
        return render_template('home.html', today_checkin=today_checkin)

    @app.route('/daily-checkin', methods=['POST'])
    @login_required
    def daily_checkin():
        feelings = request.form.get('feelings')
        mood_score = request.form.get('mood_score', type=int)
        
        # Check if already checked in today
        existing_checkin = DailyCheckIn.query.filter_by(
            user_id=current_user.id, 
            date=date.today()
        ).first()
        
        if existing_checkin:
            # Update existing check-in
            existing_checkin.feelings = feelings
            existing_checkin.mood_score = mood_score
        else:
            # Create new check-in
            checkin = DailyCheckIn(
                user_id=current_user.id,
                feelings=feelings,
                mood_score=mood_score
            )
            db.session.add(checkin)
        
        db.session.commit()
        flash('Daily check-in saved!', 'success')
        return redirect(url_for('home'))

    @app.route('/forum')
    @login_required
    def forum():
        posts = ForumPost.query.order_by(ForumPost.created_at.desc()).all()
        return render_template('forum.html', posts=posts)

    @app.route('/rewards')
    @login_required
    def rewards():
        # Get today's tasks
        tasks = DailyTask.query.filter_by(is_active=True).all()
        
        # Get user's completed tasks for today
        completed_today = UserTaskCompletion.query.filter_by(
            user_id=current_user.id,
            completed_date=date.today()
        ).all()
        
        completed_task_ids = [c.task_id for c in completed_today]
        
        return render_template('rewards.html', 
                            tasks=tasks, 
                            completed_task_ids=completed_task_ids,
                            total_points=current_user.total_points or 0)

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    
    app.run(debug=True)