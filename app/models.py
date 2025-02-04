from app import db
from datetime import datetime

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    education = db.Column(db.Text, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    projects = db.Column(db.Text, nullable=False)
    achievements = db.Column(db.Text)  # Optional
    video_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'email': self.email,
            'education': self.education,
            'cgpa': self.cgpa,
            'skills': self.skills,
            'projects': self.projects,
            'achievements': self.achievements,
            'video_path': self.video_path,
            'created_at': self.created_at.isoformat()
        }
