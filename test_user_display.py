#!/usr/bin/env python3
"""
Test script to verify user authentication and display data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import user_manager

def test_user_display():
    print("=== EcoShakti User Display Test ===\n")
    
    # Get all users
    users = user_manager.get_all_users()
    print(f"Total users found: {len(users)}\n")
    
    for user in users:
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.full_name}")
        print(f"Auth Provider: {user.auth_provider}")
        print(f"Google ID: {user.google_id}")
        print(f"Email Verified: {user.is_email_verified}")
        print(f"Grid ID: {user.grid_id}")
        print("-" * 50)
        
        # Test display logic
        if user.auth_provider == 'google':
            print("✅ This user should show GOOGLE branding:")
            print(f"   - Google icon should appear")
            print(f"   - Gmail address: {user.email}")
            print(f"   - Welcome message should mention Google login")
        else:
            print("ℹ️  This user should show standard branding:")
            print(f"   - Regular user icon")
            print(f"   - Email: {user.email}")
        print("\n")

if __name__ == "__main__":
    test_user_display()