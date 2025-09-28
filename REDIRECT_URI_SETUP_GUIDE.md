# 🔧 Google Cloud Console Redirect URI Setup

## Step-by-Step Visual Guide

### 1. Open Google Cloud Console
- Go to: https://console.cloud.google.com/
- Make sure you're in the correct project

### 2. Navigate to Credentials
```
Left Menu → APIs & Services → Credentials
```

### 3. Find Your OAuth Client ID
- Look for "OAuth 2.0 Client IDs" section
- Find the client ID that matches: 476811759857-6e2r3uvkp8gpf8nft52huoghre65s1r4.apps.googleusercontent.com
- Click the EDIT button (pencil icon)

### 4. Add Redirect URIs
In the "Authorized redirect URIs" section:

**URI 1:**
```
http://127.0.0.1:5000/callback/google
```

**URI 2:**
```
http://localhost:5000/callback/google
```

### 5. Save Changes
- Click "SAVE" at the bottom
- Wait for confirmation message

### 6. Test Again
- Go back to your EcoShakti login page
- Click "Continue with Google"
- Should now redirect to Google login page

## ✅ Success Indicators

When working correctly, you should see:
1. Click "Continue with Google" → Redirects to Google login page
2. Login with your Google account → Redirects back to EcoShakti
3. You should see: "Welcome [Your Name]! You have successfully logged in with Google."
4. You should be on the EcoShakti dashboard

## 🚨 Still Not Working?

If you still get issues, check:

1. **API Enabled**: Make sure "Google+ API" or "Google Identity API" is enabled
2. **OAuth Consent Screen**: Must be configured with app name
3. **Credentials Format**: Double-check Client ID ends with .apps.googleusercontent.com
4. **No Extra Spaces**: Make sure no extra spaces in redirect URIs

## 🔍 Debug Tips

If it's still failing:
1. Open browser Developer Tools (F12)
2. Go to Network tab
3. Click "Continue with Google"
4. Look for any error messages in the network requests
5. Check the console for JavaScript errors

The most common remaining issue is usually the OAuth consent screen not being properly configured.