from flask import Blueprint, jsonify, request, render_template, current_app, session, send_from_directory
from app.models import Candidate
from app import db
import os
from datetime import datetime

main = Blueprint('main', __name__)

# Create videos directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'videos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main.route('/')
def index():
    session.clear()  # Clear any existing session
    return render_template('index.html')

@main.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    conversation_state = session.get('state', 'initial')
    
    # Initialize session if not exists
    if 'state' not in session:
        session['state'] = 'initial'
    
    # Chatbot logic based on conversation state
    if conversation_state == 'initial':
        session['state'] = 'asking_first_name'
        return jsonify({'response': 'Welcome! I\'m excited to learn about you. Let\'s start with your first name:'})
    
    elif conversation_state == 'asking_first_name':
        session['first_name'] = message
        session['state'] = 'asking_middle_name'
        return jsonify({'response': 'Great! Do you have a middle name? If not, just type "no":'})
    
    elif conversation_state == 'asking_middle_name':
        if message.lower() != 'no':
            session['middle_name'] = message
        session['state'] = 'asking_last_name'
        return jsonify({'response': 'Now, please tell me your last name:'})
    
    elif conversation_state == 'asking_last_name':
        session['last_name'] = message
        session['state'] = 'asking_email'
        return jsonify({'response': 'Perfect! What\'s your email address?'})
    
    elif conversation_state == 'asking_email':
        session['email'] = message
        session['state'] = 'asking_education'
        return jsonify({'response': 'What\'s your highest level of education and field of study?'})
    
    elif conversation_state == 'asking_education':
        session['education'] = message
        session['state'] = 'asking_cgpa'
        return jsonify({'response': 'What was your CGPA?'})
    
    elif conversation_state == 'asking_cgpa':
        try:
            session['cgpa'] = float(message)
            session['state'] = 'asking_skills'
            return jsonify({'response': 'Impressive! Now, please list your key technical skills:'})
        except ValueError:
            return jsonify({'response': 'Please enter a valid CGPA (e.g., 3.5):'})
    
    elif conversation_state == 'asking_skills':
        session['skills'] = message
        session['state'] = 'asking_projects'
        return jsonify({'response': 'Tell me about your notable projects:'})
    
    elif conversation_state == 'asking_projects':
        session['projects'] = message
        session['state'] = 'asking_achievements'
        return jsonify({'response': 'Any achievements you\'d like to share? (Optional, type "skip" if none):'})
    
    elif conversation_state == 'asking_achievements':
        if message.lower() != 'skip':
            session['achievements'] = message
        session['state'] = 'asking_video'
        return jsonify({'response': f'Thank you, {session.get("first_name")}! Finally, I\'d like you to record a short introduction video. Click the "Record Video" button when you\'re ready.'})
    
    elif conversation_state == 'asking_video':
        session['state'] = 'video_requested'
        return jsonify({'response': 'Please click the "Record Video" button to record your introduction video.'})
    
    elif conversation_state == 'video_recorded':
        session['state'] = 'completed'
        full_name = f"{session.get('first_name')} {session.get('middle_name', '')} {session.get('last_name')}".strip()
        return jsonify({'response': f'Thank you, {full_name}! Your application has been successfully submitted. We appreciate your time and will review your application soon.'})
    
    else:
        return jsonify({'response': "I didn't quite catch that. Could you please repeat?"})

@main.route('/api/upload-video', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        # Create a unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'video_{timestamp}.webm'
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the video file
        video_file.save(video_path)
        
        # Store the relative path in session
        session['video_path'] = f'/static/videos/{filename}'
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'video_path': session['video_path']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/save-candidate', methods=['POST'])
def save_candidate():
    try:
        candidate = Candidate(
            first_name=session.get('first_name'),
            middle_name=session.get('middle_name'),
            last_name=session.get('last_name'),
            email=session.get('email'),
            education=session.get('education'),
            cgpa=session.get('cgpa'),
            skills=session.get('skills'),
            projects=session.get('projects'),
            achievements=session.get('achievements'),
            video_path=session.get('video_path')
        )
        
        db.session.add(candidate)
        db.session.commit()
        
        return jsonify({'message': 'Candidate information saved successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@main.route('/api/candidates', methods=['GET'])
def get_candidates():
    try:
        candidates = Candidate.query.all()
        return jsonify([c.to_dict() for c in candidates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/admin/candidates', methods=['GET'])
def view_candidates():
    try:
        candidates = Candidate.query.all()
        return render_template('candidates.html', candidates=[c.to_dict() for c in candidates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
