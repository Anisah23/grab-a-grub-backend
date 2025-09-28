#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    print("Starting Flask server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required packages:")
    print("pip install flask flask-restful flask-sqlalchemy flask-migrate flask-cors flask-bcrypt sqlalchemy-serializer python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)