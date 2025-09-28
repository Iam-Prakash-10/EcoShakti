from flask_login import UserMixin
import bcrypt
import json
import os
from datetime import datetime, timedelta
import secrets
import string

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at=None, 
                 full_name=None, phone_number=None, address=None, pincode=None, state=None, grid_id=None,
                 is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.now().isoformat()
        # Personal information fields
        self.full_name = full_name or username
        self.phone_number = phone_number
        self.address = address
        self.pincode = pincode
        self.state = state
        self.grid_id = grid_id or self._generate_grid_id()
        # Admin field
        self.is_admin = is_admin
    
    def _generate_grid_id(self):
        """Generate a unique grid ID for the user"""
        import random
        import string
        prefix = f"GRID-{self.id}"
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{suffix}"
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'address': self.address,
            'pincode': self.pincode,
            'state': self.state,
            'grid_id': self.grid_id,
            'is_admin': self.is_admin
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user object from dictionary"""
        return cls(
            id=data['id'],
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            created_at=data.get('created_at'),
            full_name=data.get('full_name'),
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            pincode=data.get('pincode'),
            state=data.get('state'),
            grid_id=data.get('grid_id'),
            is_admin=data.get('is_admin', False)
        )

class UserManager:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.users = {}
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = User.from_dict(user_data)
                        self.users[user.id] = user
            except (json.JSONDecodeError, KeyError):
                self.users = {}
    
    def save_users(self):
        """Save users to JSON file"""
        users_data = [user.to_dict() for user in self.users.values()]
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    

    

    

    
    def create_user(self, username, email, password, is_admin=False):
        """Create a new user"""
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == username:
                raise ValueError("Username already exists")
            if user.email == email:
                raise ValueError("Email already exists")
        
        # Remove email whitelist check since admin panel is removed
        # Allow any valid email to register
        
        # Generate new user ID
        user_id = str(len(self.users) + 1)
        
        # Hash password
        password_hash = User.hash_password(password)
        
        # Create user
        user = User(
            user_id, username, email, password_hash, is_admin=is_admin
        )
        self.users[user_id] = user
        
        # Save to file
        self.save_users()
        
        return user
    
    def get_user(self, user_id):
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate user by username/email and password"""
        user = self.get_user_by_username(username_or_email)
        if not user:
            user = self.get_user_by_email(username_or_email)
        
        if user and user.check_password(password):
            return user
        return None
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile information"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # Update profile fields if provided
        if 'full_name' in profile_data:
            user.full_name = profile_data['full_name']
        if 'phone_number' in profile_data:
            user.phone_number = profile_data['phone_number']
        if 'address' in profile_data:
            user.address = profile_data['address']
        if 'pincode' in profile_data:
            user.pincode = profile_data['pincode']
        if 'state' in profile_data:
            user.state = profile_data['state']
        
        # Save changes
        self.save_users()
        return True
    
    def delete_user(self, user_id):
        """Delete a user by ID"""
        if user_id in self.users:
            del self.users[user_id]
            self.save_users()
            return True
        return False
    
    def get_all_users(self):
        """Get all users"""
        return list(self.users.values())
    
    def export_users_csv(self):
        """Export users to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Username', 'Email', 'Full Name', 'Phone Number', 'Address', 'Pincode', 'State', 'Grid ID', 'Created At'])
        
        # Write user data
        for user in self.users.values():
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.full_name or '',
                user.phone_number or '',
                user.address or '',
                user.pincode or '',
                user.state or '',
                user.grid_id,
                user.created_at
            ])
        
        return output.getvalue()
    
    def export_users_json(self):
        """Export users to JSON format (without password hashes for security)"""
        users_data = []
        for user in self.users.values():
            user_dict = user.to_dict()
            # Remove password hash for security
            user_dict.pop('password_hash', None)
            users_data.append(user_dict)
        
        return json.dumps(users_data, indent=2)
    
    def import_users_from_json(self, json_data, overwrite_existing=False):
        """Import users from JSON data"""
        try:
            users_data = json.loads(json_data) if isinstance(json_data, str) else json_data
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for user_data in users_data:
                try:
                    # Check if user already exists
                    existing_user = self.get_user_by_username(user_data.get('username', '')) or \
                                  self.get_user_by_email(user_data.get('email', ''))
                    
                    if existing_user and not overwrite_existing:
                        skipped_count += 1
                        continue
                    
                    # Generate new ID if not provided or if user exists
                    if not user_data.get('id') or existing_user:
                        user_data['id'] = str(len(self.users) + imported_count + 1)
                    
                    # If no password hash provided, generate a default one
                    if not user_data.get('password_hash'):
                        user_data['password_hash'] = User.hash_password('defaultpassword123')
                    
                    # Create user object
                    user = User.from_dict(user_data)
                    
                    # Add or update user
                    self.users[user.id] = user
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Error importing user {user_data.get('username', 'unknown')}: {str(e)}")
            
            # Save changes
            if imported_count > 0:
                self.save_users()
            
            return {
                'success': True,
                'imported': imported_count,
                'skipped': skipped_count,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to parse JSON data: {str(e)}"
            }
    
    def import_users_from_csv(self, csv_data, overwrite_existing=False):
        """Import users from CSV data"""
        import csv
        import io
        
        try:
            csv_file = io.StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for row in reader:
                try:
                    # Check if user already exists
                    existing_user = self.get_user_by_username(row.get('Username', '')) or \
                                  self.get_user_by_email(row.get('Email', ''))
                    
                    if existing_user and not overwrite_existing:
                        skipped_count += 1
                        continue
                    
                    # Create user data
                    user_data = {
                        'id': row.get('ID') or str(len(self.users) + imported_count + 1),
                        'username': row['Username'],
                        'email': row['Email'],
                        'password_hash': User.hash_password('defaultpassword123'),  # Default password
                        'full_name': row.get('Full Name', ''),
                        'phone_number': row.get('Phone Number', ''),
                        'address': row.get('Address', ''),
                        'pincode': row.get('Pincode', ''),
                        'state': row.get('State', ''),
                        'grid_id': row.get('Grid ID', ''),
                        'created_at': row.get('Created At') or datetime.now().isoformat()
                    }
                    
                    # Create user object
                    user = User.from_dict(user_data)
                    
                    # Add or update user
                    self.users[user.id] = user
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Error importing user {row.get('Username', 'unknown')}: {str(e)}")
            
            # Save changes
            if imported_count > 0:
                self.save_users()
            
            return {
                'success': True,
                'imported': imported_count,
                'skipped': skipped_count,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to parse CSV data: {str(e)}"
            }
    
# Global user manager instance
user_manager = UserManager()
