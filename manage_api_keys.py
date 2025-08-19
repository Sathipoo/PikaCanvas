#!/usr/bin/env python3
"""
API Key Management Utility for PikaCanvas

This script helps manage API keys for users in the PikaCanvas system.
"""

import os
import sys
import hashlib
import secrets
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def create_app_context():
    """Create Flask app context for database operations"""
    from app import create_app
    from app.models.database import db
    
    app = create_app()
    return app, db

def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key):
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key_for_user(username, key_name="Default"):
    """Create an API key for a user"""
    app, db = create_app_context()
    
    with app.app_context():
        from app.models.database import User, APIKey
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found")
            return None
        
        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        # Create API key record
        api_key_record = APIKey(
            key_hash=key_hash,
            user_id=user.id,
            name=key_name,
            is_active=True
        )
        
        db.session.add(api_key_record)
        db.session.commit()
        
        print(f"✅ API key created for user '{username}'")
        print(f"🔑 Key Name: {key_name}")
        print(f"🔑 API Key: {api_key}")
        print("⚠️  Save this key securely - it won't be shown again!")
        
        return api_key

def list_api_keys_for_user(username):
    """List all API keys for a user"""
    app, db = create_app_context()
    
    with app.app_context():
        from app.models.database import User, APIKey
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        # Get API keys
        api_keys = APIKey.query.filter_by(user_id=user.id).all()
        
        if not api_keys:
            print(f"📝 No API keys found for user '{username}'")
            return
        
        print(f"🔑 API Keys for user '{username}':")
        print("-" * 50)
        for key in api_keys:
            status = "✅ Active" if key.is_active else "❌ Inactive"
            last_used = key.last_used.strftime("%Y-%m-%d %H:%M") if key.last_used else "Never"
            print(f"Name: {key.name}")
            print(f"Status: {status}")
            print(f"Created: {key.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"Last Used: {last_used}")
            print("-" * 30)

def deactivate_api_key(username, key_name):
    """Deactivate an API key"""
    app, db = create_app_context()
    
    with app.app_context():
        from app.models.database import User, APIKey
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        # Find the API key
        api_key = APIKey.query.filter_by(user_id=user.id, name=key_name).first()
        if not api_key:
            print(f"❌ API key '{key_name}' not found for user '{username}'")
            return
        
        api_key.is_active = False
        db.session.commit()
        
        print(f"✅ API key '{key_name}' deactivated for user '{username}'")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("🎨 PikaCanvas API Key Manager")
        print("=" * 40)
        print("Usage:")
        print("  python manage_api_keys.py create <username> [key_name]")
        print("  python manage_api_keys.py list <username>")
        print("  python manage_api_keys.py deactivate <username> <key_name>")
        print("\nExamples:")
        print("  python manage_api_keys.py create admin 'Production Key'")
        print("  python manage_api_keys.py list admin")
        print("  python manage_api_keys.py deactivate admin 'Old Key'")
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        if len(sys.argv) < 3:
            print("❌ Username required")
            return
        username = sys.argv[2]
        key_name = sys.argv[3] if len(sys.argv) > 3 else "Default"
        create_api_key_for_user(username, key_name)
    
    elif command == "list":
        if len(sys.argv) < 3:
            print("❌ Username required")
            return
        username = sys.argv[2]
        list_api_keys_for_user(username)
    
    elif command == "deactivate":
        if len(sys.argv) < 4:
            print("❌ Username and key name required")
            return
        username = sys.argv[2]
        key_name = sys.argv[3]
        deactivate_api_key(username, key_name)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: create, list, deactivate")

if __name__ == "__main__":
    main()