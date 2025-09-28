# EcoShakti Email & Google OAuth Setup Guide

## 🚨 IMPORTANT: You need to update your .env file with real credentials!

Your current `.env` file has placeholder/demo values that won't work. Here's how to fix both issues:

---

## 📧 **ISSUE 1: Email Verification Not Working**

### **Problem:** 
Email verification links are not being sent because your email configuration uses demo values.

### **Solution:**

1. **Get Gmail App Password:**
   - Go to your Google Account settings: https://myaccount.google.com/
   - Security → 2-Step Verification → App passwords
   - Generate an app password for "Mail"

2. **Update your `.env` file:**
   ```bash
   # Replace these lines in your .env file:
   MAIL_USERNAME=your_real_email@gmail.com
   MAIL_PASSWORD=your_16_character_app_password
   MAIL_DEFAULT_SENDER=your_real_email@gmail.com
   ```

### **Example:**
```bash
MAIL_USERNAME=john.doe@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_DEFAULT_SENDER=john.doe@gmail.com
```

---

## 🔐 **ISSUE 2: Google OAuth Not Working**

### **Problem:** 
Your Google OAuth credentials appear to be incorrect or placeholder values.

### **Solution:**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Google Identity API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" or "Google Identity"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add these **Authorized redirect URIs**:
     ```
     http://127.0.0.1:5000/callback/google
     http://localhost:5000/callback/google
     ```
   - Click "Create"

4. **Copy Your Credentials:**
   - Client ID format: `123456789-abc...xyz.apps.googleusercontent.com`
   - Client Secret format: `GOCSPX-abc...xyz`

5. **Update your `.env` file:**
   ```bash
   # Replace these lines in your .env file:
   GOOGLE_CLIENT_ID=123456789-your_actual_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your_actual_client_secret
   ```

---

## ⚡ **Quick Fix for Testing**

If you want to test the app immediately without setting up email/OAuth:

1. **Register a new account** - it will auto-verify (no email needed)
2. **Use regular username/password login** - works without OAuth
3. **Set up email/OAuth later** when you have the credentials

---

## 🧪 **How to Test**

1. **Update your `.env` file** with real credentials
2. **Restart the application:**
   ```bash
   python app.py
   ```
3. **Check the debug panel** on login page for configuration status
4. **Try registering** - you should receive an email
5. **Try Google OAuth** - should redirect to Google

---

## 🔍 **Debug Information**

The login page now shows a debug panel with:
- ✅ = Configured correctly
- ❌ = Needs to be updated

Look for:
- Email Configured: ✅/❌
- Google Client ID: ✅/❌  
- Google Secret: ✅/❌
- OAuth Ready: ✅/❌

---

## 📞 **Need Help?**

If you're still having issues:
1. Check the debug panel on the login page
2. Look at the terminal for error messages
3. Make sure your credentials are in the correct format
4. Verify redirect URIs match exactly in Google Cloud Console