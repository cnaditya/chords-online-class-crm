#!/usr/bin/env python3
"""
Chords Music Academy CRM - Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup environment and create necessary directories"""
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    uploads_dir = data_dir / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    # Create .env if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("Created .env file from .env.example")
            print("Please update .env with your settings before running the app")
            return False
    
    return True

def run_migrations():
    """Run database migrations"""
    try:
        # Import here to ensure models are loaded
        from models.base import engine, Base
        import models
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {e}")
        return False

def main():
    """Main startup function"""
    print("🎵 Chords Music Academy CRM - Starting up...")
    
    # Setup environment
    if not setup_environment():
        return
    
    # Run migrations
    if not run_migrations():
        print("Failed to setup database. Please check your configuration.")
        return
    
    # Start Streamlit app
    print("Starting Streamlit application...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")

if __name__ == "__main__":
    main()