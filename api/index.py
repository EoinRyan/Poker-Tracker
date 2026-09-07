import sys
import os

# Add the project root to the path so Flask can find app.py and all modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel calls the `app` object as a WSGI handler
# No extra wrapper needed — @vercel/python handles WSGI natively
