# Google OAuth Setup Guide for EcoShakti

## Quick Setup Instructions

### Step 1: Create Google OAuth Credentials

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create or select a project**
3. **Enable Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" or "Google Identity"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add these **Authorized redirect URIs**:
     ```
     http://127.0.0.1:5000/callback/google
     http://localhost:5000/callback/google
     ```
   - Click "Create"

### Step 2: Update Your .env File

Replace the placeholder values in your `.env` file:

```bash
# Current placeholder values (replace these):
GOOGLE_CLIENT_ID=your_actual_google_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here

# With your actual credentials (example format):
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz123456
```

### Step 3: Restart Your Application

After updating the credentials:
```bash
python app.py
```

### Step 4: Test Google Login

1. Visit http://127.0.0.1:5000
2. Click "Continue with Google"
3. Complete the OAuth flow

## Notes

- The "Continue with Google" button is now always visible
- If credentials are not configured, users will see helpful error messages
- The system will guide users to update their configuration
- All other authentication features (email/password, forgot password) work independently

## Troubleshooting

- **Error: "OAuth service unavailable"** → Check your credentials format
- **Error: "Credentials need to be updated"** → Replace placeholder values
- **Error: "OAuth not configured"** → Add credentials to .env file
- **Redirect URI mismatch** → Ensure URIs match exactly in Google Cloud Console