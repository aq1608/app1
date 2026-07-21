from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
from datetime import datetime, date, timedelta
import re

app = Flask(__name__)
app.secret_key = 'simple-secret-key'

# Simple data storage functions
def load_data(filename):
    filepath = f'data/{filename}'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    os.makedirs('data', exist_ok=True)
    with open(f'data/{filename}', 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_current_user():
    if 'user_id' in session:
        users = load_data('users.json')
        return next((u for u in users if u['id'] == session['user_id']), None)
    return None

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_data('users.json')
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        
        if user:
            session['user_id'] = user['id']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_data('users.json')
        
        # Simple user creation
        new_user = {
            'id': len(users) + 1,
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password'],  # No encryption for testing
            'phone': request.form.get('phone', ''),
            'birthday': request.form.get('birthday', ''),
            'created_at': datetime.now().isoformat(),
            'questionnaire_completed': False,
            'total_points': 0
        }
        
        users.append(new_user)
        save_data('users.json', users)
        
        session['user_id'] = new_user['id']
        flash('Registration successful!', 'success')
        return redirect(url_for('questionnaire'))
    
    return render_template('register.html')

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        users = load_data('users.json')
        current_user = next(u for u in users if u['id'] == session['user_id'])
        
        current_user['mental_illness'] = request.form.get('mental_illness', '')
        current_user['preferred_gender'] = request.form.get('preferred_gender', '')
        current_user['preferred_language'] = request.form.get('preferred_language', '')
        current_user['questionnaire_completed'] = True
        
        save_data('users.json', users)
        flash('Questionnaire completed!', 'success')
        return redirect(url_for('home'))
    
    return render_template('questionnaire.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_current_user()
    
    # Check if user did daily check-in today
    checkins = load_data('checkins.json')
    today_str = date.today().isoformat()
    today_checkin = next((c for c in checkins if c['user_id'] == user['id'] and c['date'] == today_str), None)
    
    return render_template('home.html', user=user, today_checkin=today_checkin)

@app.route('/daily-checkin', methods=['POST'])
def daily_checkin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    checkins = load_data('checkins.json')
    today_str = date.today().isoformat()
    
    new_checkin = {
        'id': len(checkins) + 1,
        'user_id': session['user_id'],
        'feelings': request.form['feelings'],
        'mood_score': int(request.form.get('mood_score', 5)),
        'date': today_str,
        'created_at': datetime.now().isoformat()
    }
    
    # Remove any existing checkin for today
    checkins = [c for c in checkins if not (c['user_id'] == session['user_id'] and c['date'] == today_str)]
    checkins.append(new_checkin)
    
    save_data('checkins.json', checkins)
    flash('Daily check-in saved!', 'success')
    return redirect(url_for('home'))

@app.route('/forum')
def forum():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    posts = load_data('posts.json')
    users = load_data('users.json')
    
    # Add username to posts
    for post in posts:
        user = next((u for u in users if u['id'] == post['user_id']), None)
        post['username'] = user['username'] if user else 'Unknown'
    
    return render_template('forum.html', posts=posts)

@app.route('/forum/new', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        posts = load_data('posts.json')
        
        new_post = {
            'id': len(posts) + 1,
            'user_id': session['user_id'],
            'title': request.form['title'],
            'content': request.form['content'],
            'likes': 0,
            'created_at': datetime.now().isoformat()
        }
        
        posts.append(new_post)
        save_data('posts.json', posts)
        flash('Post created!', 'success')
        return redirect(url_for('forum'))
    
    return render_template('new_post.html')

@app.route('/rewards')
def rewards():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_current_user()
    
    # Sample tasks
    tasks = [
        {'id': 1, 'name': 'Write down your feelings for today', 'points': 10},
        {'id': 2, 'name': 'Tell us more about your day in the forum', 'points': 10},
        {'id': 3, 'name': 'Donate through our app to help others in need', 'points': 10}
    ]
    
    # Get today's completed tasks
    completions = load_data('task_completions.json')
    today_str = date.today().isoformat()
    completed_today = [c['task_id'] for c in completions if 
                      c['user_id'] == user['id'] and c['date'] == today_str]
    
    # Check if user has done daily check-in today
    checkins = load_data('checkins.json')
    has_checkin_today = any(c['user_id'] == user['id'] and c['date'] == today_str for c in checkins)
    
    # Check if user has posted in forum
    posts = load_data('posts.json')
    has_post_today = any(p['user_id'] == user['id'] and p['created_at'][:10] == today_str for p in posts)
    
    # Update task availability
    for task in tasks:
        task['completed'] = task['id'] in completed_today
        if task['id'] == 1:  # Daily check-in task
            task['available'] = has_checkin_today
        elif task['id'] == 2:  # Forum post task
            task['available'] = has_post_today
        else:  # Donation task
            task['available'] = True  # Always available for demo
    
    completed_count = len(completed_today)
    
    return render_template('rewards.html', 
                         user=user, 
                         tasks=tasks, 
                         completed_count=completed_count,
                         total_tasks=len(tasks))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_current_user()
    posts = load_data('posts.json')
    checkins = load_data('checkins.json')
    
    user_posts = len([p for p in posts if p['user_id'] == user['id']])
    user_checkins = len([c for c in checkins if c['user_id'] == user['id']])
    
    return render_template('profile.html', user=user, total_posts=user_posts, total_checkins=user_checkins)

@app.route('/complete-task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    # Load task completions
    completions = load_data('task_completions.json')
    
    # Check if already completed today
    today_str = date.today().isoformat()
    existing = next((c for c in completions if 
                    c['user_id'] == session['user_id'] and 
                    c['task_id'] == task_id and 
                    c['date'] == today_str), None)
    
    if existing:
        return {'error': 'Task already completed today'}, 400
    
    # Task definitions
    tasks = {
        1: {'name': 'Write down your feelings for today', 'points': 10},
        2: {'name': 'Tell us more about your day in the forum', 'points': 10},
        3: {'name': 'Donate through our app to help others in need', 'points': 10}
    }
    
    if task_id not in tasks:
        return {'error': 'Invalid task'}, 400
    
    # Add completion
    completion = {
        'id': len(completions) + 1,
        'user_id': session['user_id'],
        'task_id': task_id,
        'date': today_str,
        'points_earned': tasks[task_id]['points'],
        'completed_at': datetime.now().isoformat()
    }
    
    completions.append(completion)
    save_data('task_completions.json', completions)
    
    # Update user points
    users = load_data('users.json')
    user = next(u for u in users if u['id'] == session['user_id'])
    user['total_points'] = user.get('total_points', 0) + tasks[task_id]['points']
    save_data('users.json', users)
    
    return {
        'success': True, 
        'points_earned': tasks[task_id]['points'],
        'total_points': user['total_points']
    }

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_current_user()
    
    # Load chat history
    chats = load_data('chats.json')
    user_chats = [c for c in chats if c['user_id'] == user['id']]
    
    return render_template('chatbot.html', user=user, chats=user_chats)

@app.route('/chat/send', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    user = get_current_user()
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return {'error': 'Message cannot be empty'}, 400
    
    # Load existing chats
    chats = load_data('chats.json')
    
    # Save user message
    user_chat = {
        'id': len(chats) + 1,
        'user_id': user['id'],
        'message': user_message,
        'is_bot': False,
        'timestamp': datetime.now().isoformat()
    }
    chats.append(user_chat)
    
    # Generate bot response
    bot_response = generate_bot_response(user_message, user)
    
    # Save bot response
    bot_chat = {
        'id': len(chats) + 1,
        'user_id': user['id'],
        'message': bot_response['message'],
        'is_bot': True,
        'needs_therapist': bot_response.get('needs_therapist', False),
        'crisis_detected': bot_response.get('crisis_detected', False),
        'timestamp': datetime.now().isoformat()
    }
    chats.append(bot_chat)
    
    save_data('chats.json', chats)
    
    return {
        'user_message': user_message,
        'bot_response': bot_response['message'],
        'needs_therapist': bot_response.get('needs_therapist', False),
        'crisis_detected': bot_response.get('crisis_detected', False)
    }

def generate_bot_response(message, user):
    """Generate intelligent bot responses based on user input"""
    message_lower = message.lower()
    
    # Crisis keywords detection
    crisis_keywords = [
        'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm', 
        'want to die', 'no point', 'give up', 'hopeless', 'worthless'
    ]
    
    # Check for crisis
    if any(keyword in message_lower for keyword in crisis_keywords):
        return {
            'message': "I'm really concerned about what you're going through right now. Your feelings are valid, but you don't have to face this alone. Would you like me to connect you with one of our professional therapists immediately? They're trained to help in situations like this. 💙",
            'crisis_detected': True,
            'needs_therapist': True
        }
    
    # Emotional keywords
    sad_keywords = ['sad', 'depressed', 'down', 'lonely', 'empty', 'crying', 'tears']
    anxious_keywords = ['anxious', 'worried', 'panic', 'scared', 'afraid', 'nervous', 'stress']
    angry_keywords = ['angry', 'mad', 'furious', 'hate', 'frustrated', 'annoyed']
    happy_keywords = ['happy', 'good', 'great', 'awesome', 'amazing', 'wonderful', 'excited']
    
    # Get user's recent mood from check-ins
    checkins = load_data('checkins.json')
    recent_checkin = None
    today = datetime.now().date()
    for checkin in reversed(checkins):
        if (checkin['user_id'] == user['id'] and 
            datetime.fromisoformat(checkin['date']).date() >= today - timedelta(days=3)):
            recent_checkin = checkin
            break
    
    # Personalized responses based on emotion detection
    if any(keyword in message_lower for keyword in sad_keywords):
        responses = [
            f"I hear that you're feeling sad, {user['username']}. That's completely okay - sadness is a natural human emotion. Sometimes it helps to talk about what's making you feel this way. What's been on your mind lately? 🤗",
            f"I'm sorry you're going through a tough time, {user['username']}. Remember that it's okay to feel sad, and these feelings will pass. Have you tried any self-care activities today? Maybe a walk or listening to music? 💙",
            "Sadness can feel overwhelming, but you're stronger than you know. Would you like some suggestions for coping strategies, or would you prefer to talk about what's troubling you?"
        ]
        return {'message': responses[hash(message) % len(responses)]}
    
    elif any(keyword in message_lower for keyword in anxious_keywords):
        responses = [
            f"I can sense you're feeling anxious, {user['username']}. Anxiety can be really challenging. Let's try a quick breathing exercise: breathe in for 4 counts, hold for 4, then breathe out for 4. Want to try this with me? 🌸",
            "Anxiety is tough, but you're tougher. Try to focus on what you can control right now. What's one small thing you can do today to take care of yourself?",
            f"I understand anxiety can be overwhelming, {user['username']}. Sometimes it helps to ground yourself - can you name 5 things you can see around you right now? This can help bring you back to the present moment. ✨"
        ]
        return {'message': responses[hash(message) % len(responses)]}
    
    elif any(keyword in message_lower for keyword in angry_keywords):
        responses = [
            f"I can feel that you're angry, {user['username']}. Anger is a valid emotion, and it's okay to feel this way. Sometimes anger is trying to tell us something important. What's making you feel this way? 🔥➡️💙",
            "Anger can be intense. It might help to take some deep breaths or do some physical activity to release that energy. Want to talk about what's frustrating you?",
            f"I hear your frustration, {user['username']}. Sometimes anger is actually sadness or hurt in disguise. What's really bothering you underneath all that anger?"
        ]
        return {'message': responses[hash(message) % len(responses)]}
    
    elif any(keyword in message_lower for keyword in happy_keywords):
        responses = [
            f"I love hearing that you're feeling good, {user['username']}! Happiness looks beautiful on you. What's bringing you joy today? 😊✨",
            f"That's wonderful, {user['username']}! It's so important to celebrate the good moments. Care to share what's making you happy?",
            "I'm so glad you're having a good day! Remember to savor these positive feelings - they're just as important as processing the difficult ones. 🌟"
        ]
        return {'message': responses[hash(message) % len(responses)]}
    
    # Therapy-related keywords
    therapy_keywords = ['therapist', 'therapy', 'counselor', 'help', 'professional', 'talk to someone']
    if any(keyword in message_lower for keyword in therapy_keywords):
        return {
            'message': f"I think it's great that you're considering professional support, {user['username']}! Speaking with a therapist can be incredibly helpful. Based on your profile, I can connect you with a therapist who matches your preferences. Would you like me to find someone for you? 🤝",
            'needs_therapist': True
        }
    
    # Greeting responses
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(greeting in message_lower for greeting in greetings):
        time_of_day = datetime.now().hour
        if time_of_day < 12:
            greeting = "Good morning"
        elif time_of_day < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        mood_context = ""
        if recent_checkin and recent_checkin.get('mood_score'):
            if recent_checkin['mood_score'] >= 8:
                mood_context = " I saw you've been feeling pretty good lately - that's wonderful! "
            elif recent_checkin['mood_score'] <= 4:
                mood_context = " I noticed you've been having some tough days lately. I'm here for you. "
        
        return {
            'message': f"{greeting}, {user['username']}! 😊 How may I help you today?{mood_context}Feel free to share what's on your mind, or ask me anything about mental health and wellness. 💙"
        }
    
    # Default supportive responses
    default_responses = [
        f"I hear you, {user['username']}. Tell me more about what you're experiencing. I'm here to listen and support you. 💙",
        f"Thank you for sharing that with me, {user['username']}. How are you feeling about this situation? Sometimes talking through our thoughts can help us see things more clearly. 🤗",
        f"I appreciate you opening up, {user['username']}. What would be most helpful for you right now - would you like some coping strategies, or do you just need someone to listen? ✨",
        f"That sounds like a lot to handle, {user['username']}. You're not alone in this. What kind of support would feel most helpful to you right now? 🌟"
    ]
    
    return {'message': default_responses[hash(message) % len(default_responses)]}

@app.route('/connect-therapist', methods=['POST'])
def connect_therapist():
    if 'user_id' not in session:
        return {'error': 'Not logged in'}, 401
    
    user = get_current_user()
    
    # For now, simulate connecting to a therapist
    # In real implementation, this would match with actual therapist availability
    
    therapist_names = ["Dr. Sarah Chen", "Healing Henry", "Dr. Maria Rodriguez", "Dr. James Wilson"]
    selected_therapist = therapist_names[hash(user['username']) % len(therapist_names)]
    
    return {
        'success': True,
        'therapist_name': selected_therapist,
        'message': f"Great! I'm connecting you with {selected_therapist} right now. They should be available for a chat within the next few minutes. You'll receive a notification when they're ready to talk. 💙"
    }

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)