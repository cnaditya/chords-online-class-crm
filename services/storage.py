import os
import shutil
from pathlib import Path
from typing import Optional
from config import Config

class StorageService:
    def __init__(self):
        self.upload_dir = Path(Config.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_content: bytes, filename: str, subfolder: str = "") -> str:
        """Save file to local storage and return file path"""
        if subfolder:
            save_dir = self.upload_dir / subfolder
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.upload_dir
        
        file_path = save_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return str(file_path)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """Get URL for file access (for local files, return relative path)"""
        return file_path.replace(str(self.upload_dir), "/uploads")
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(file_path)