from app import create_app
from app.models import Candidate

def view_database():
    app = create_app()
    with app.app_context():
        print("\n=== Database Contents ===\n")
        candidates = Candidate.query.all()
        if not candidates:
            print("No candidates found in database.")
            return
        
        for candidate in candidates:
            print(f"ID: {candidate.id}")
            print(f"Name: {candidate.first_name} {candidate.middle_name or ''} {candidate.last_name}")
            print(f"Email: {candidate.email}")
            print(f"Education: {candidate.education}")
            print(f"CGPA: {candidate.cgpa}")
            print(f"Skills: {candidate.skills}")
            print(f"Projects: {candidate.projects}")
            print(f"Achievements: {candidate.achievements}")
            print(f"Video Path: {candidate.video_path}")
            print("-" * 50)

if __name__ == "__main__":
    view_database()
