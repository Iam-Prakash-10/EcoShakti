# 🔐 Complete Google OAuth Setup for EcoShakti

## 📋 **What You'll Need**
- Google account
- 10-15 minutes to complete setup
- Access to Google Cloud Console

---

## 🚀 **Step 1: Create Google Cloud Project**

1. **Visit Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click "Select a project" → "New Project"
   - Project name: `EcoShakti-OAuth` (or any name you prefer)
   - Click "Create"
   - Wait for project creation (1-2 minutes)

---

## 🔑 **Step 2: Enable Google Identity API**

1. **Navigate to APIs & Services**
   - In the left sidebar: "APIs & Services" → "Library"

2. **Enable Required API**
   - Search for: "Google+ API" or "Google Identity"
   - Click on "Google+ API"
   - Click "Enable" button
   - Wait for activation (30 seconds)

---

## 🛡️ **Step 3: Configure OAuth Consent Screen**

1. **Go to OAuth Consent Screen**
   - Left sidebar: "APIs & Services" → "OAuth consent screen"

2. **Choose User Type**
   - Select "External" (for testing)
   - Click "Create"

3. **Fill Required Fields**
   - App name: `EcoShakti`
   - User support email: `your-email@gmail.com`
   - Developer contact: `your-email@gmail.com`
   - Click "Save and Continue"

4. **Skip Scopes** (Click "Save and Continue")

5. **Add Test Users** (for development)
   - Add your own email address
   - Click "Save and Continue"

---

## 🔐 **Step 4: Create OAuth 2.0 Credentials**

1. **Go to Credentials**
   - Left sidebar: "APIs & Services" → "Credentials"

2. **Create Credentials**
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"

3. **Configure Application**
   - Application type: "Web application"
   - Name: `EcoShakti Web Client`

4. **Add Authorized Redirect URIs** (CRITICAL!)
   ```
   http://127.0.0.1:5000/callback/google
   http://localhost:5000/callback/google
   ```
   - Click "Add URI" for each one
   - Make sure there are NO extra spaces or characters

5. **Create Credentials**
   - Click "Create"
   - **COPY THE CREDENTIALS** immediately:
     - Client ID: `123456789-abc...xyz.apps.googleusercontent.com`
     - Client Secret: `GOCSPX-abc...xyz`

---

## 📝 **Step 5: Update Your .env File**

Replace these lines in your `.env` file:

```bash
# Before (placeholder values):
GOOGLE_CLIENT_ID=your_actual_google_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here

# After (your real credentials):
GOOGLE_CLIENT_ID=123456789-your_actual_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_actual_client_secret
```

**Important Format Check:**
- ✅ Client ID ends with `.apps.googleusercontent.com`
- ✅ Client Secret starts with `GOCSPX-`

---

## 🧪 **Step 6: Test the Setup**

1. **Restart Your Application**
   ```bash
   python app.py
   ```

2. **Visit Login Page**
   - Go to: http://127.0.0.1:5000
   - Check debug panel for OAuth status

3. **Test Google Login**
   - Click "Continue with Google"
   - Should redirect to Google authentication
   - After login, should return to EcoShakti dashboard

---

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **"redirect_uri_mismatch" Error**
   - Check redirect URIs in Google Cloud Console match exactly:
   - `http://127.0.0.1:5000/callback/google`
   - `http://localhost:5000/callback/google`

2. **"OAuth Error" or "Invalid Client"**
   - Verify Client ID format: ends with `.apps.googleusercontent.com`
   - Verify Client Secret format: starts with `GOCSPX-`
   - Check for extra spaces or characters

3. **"This app isn't verified"**
   - Normal for development
   - Click "Advanced" → "Go to EcoShakti (unsafe)"
   - For production, submit for verification

### **Debug Checklist:**
- [ ] Google+ API is enabled
- [ ] OAuth consent screen is configured
- [ ] Redirect URIs are exact matches
- [ ] Credentials are in correct format
- [ ] No extra spaces in .env file

---

## 🎯 **Success Indicators**

When properly configured, you should see:
- ✅ OAuth Ready: ✅ (in debug panel)
- Google login redirects to actual Google page
- After Google login, user is created in EcoShakti
- User sees EcoShakti dashboard with their Google name

---

## 📞 **Need Help?**

If you encounter issues:
1. Check the application terminal for error messages
2. Look at the debug panel on login page
3. Verify all credentials are copied correctly
4. Ensure redirect URIs match exactly

**This guide will get your Google authentication working perfectly! 🚀**