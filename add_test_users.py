#!/usr/bin/env python3
"""
Script to add multiple Gmail users for testing the account selection feature
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user import user_manager

def add_test_gmail_users():
    """Add multiple test Gmail users"""
    
    # List of test Gmail users to add
    test_users = [
        {
            'username': 'Sarah Johnson',
            'email': 'sarah.johnson.energy@gmail.com',
            'full_name': 'Sarah Johnson',
            'google_id': '110123456789012345678',
        },
        {
            'username': 'Mike Chen',
            'email': 'mike.chen.solar@gmail.com', 
            'full_name': 'Mike Chen',
            'google_id': '110987654321098765432',
        },
        {
            'username': 'Emily Davis',
            'email': 'emily.davis.renewable@gmail.com',
            'full_name': 'Emily Davis', 
            'google_id': '110555666777888999000',
        },
        {
            'username': 'Alex Wilson',
            'email': 'alex.wilson.grid@gmail.com',
            'full_name': 'Alex Wilson',
            'google_id': '110444555666777888999',
        },
        {
            'username': 'Jessica Brown',
            'email': 'jessica.brown.eco@gmail.com',
            'full_name': 'Jessica Brown',
            'google_id': '110333444555666777888',
        }
    ]
    
    print("=== Adding Test Gmail Users ===\n")
    
    for user_data in test_users:
        try:
            # Check if user already exists
            existing_user = user_manager.get_user_by_email(user_data['email'])
            if existing_user:
                print(f"⚠️  User {user_data['email']} already exists - skipping")
                continue
                
            # Create new Google user
            user = user_manager.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=None,  # No password for Google users
                google_id=user_data['google_id'],
                auth_provider='google'
            )
            
            # Update full name
            user.full_name = user_data['full_name']
            user.is_email_verified = True  # Auto-verify Google accounts
            
            print(f"✅ Added Gmail user: {user_data['full_name']} ({user_data['email']})")
            
        except Exception as e:
            print(f"❌ Error adding user {user_data['email']}: {e}")
    
    # Save all changes
    user_manager.save_users()
    print(f"\n✅ All users saved successfully!")
    
    # Display all Gmail users
    print("\n=== All Gmail Users in System ===")
    gmail_users = [user for user in user_manager.get_all_users() if user.auth_provider == 'google']
    
    for i, user in enumerate(gmail_users, 1):
        print(f"{i}. {user.full_name}")
        print(f"   📧 {user.email}")
        print(f"   🆔 Grid ID: {user.grid_id}")
        print(f"   🔑 Google ID: {user.google_id}")
        print("")

if __name__ == "__main__":
    add_test_gmail_users()