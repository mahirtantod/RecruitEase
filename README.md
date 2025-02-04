# RecruitEase - Interactive Recruitment Chatbot

A modern recruitment chatbot system that interacts with candidates, collects their information, and records introduction videos.

## Features

- Interactive chatbot for candidate screening
- Basic information collection (name, education, skills)
- Live video recording for candidate introductions
- User-friendly interface
- Data storage for candidate information

## Project Structure

```
RecruitEase/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   └── index.html
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── chatbot.py
├── instance/
├── requirements.txt
├── config.py
└── run.py
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python run.py
   ```

## Technology Stack

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLAlchemy
- Video Handling: OpenCV
- UI Framework: Bootstrap

## Development Status

Current Version: 1.0.0 (Basic Chatbot Implementation)
