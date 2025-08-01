# Google OAuth Setup Guide

This guide will help you set up Google OAuth for your GSale application.

## Prerequisites

1. A Google account
2. Access to Google Cloud Console
3. Your Flask application running

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" and then "New Project"
3. Enter a project name (e.g., "GSale App")
4. Click "Create"

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google+ API" or "Google Identity"
3. Click on "Google Identity" and enable it

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: GSale
   - User support email: Your email
   - Developer contact information: Your email
   - Save and continue through the steps

4. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Name: GSale Web App
   - Authorized JavaScript origins: 
     - `http://localhost:5000` (for development)
     - `http://gsale.levimylesllc.com` (for production)
     - `https://gsale.levimylesllc.com` (for production, if using HTTPS)
   - Authorized redirect URIs:
     - `http://localhost:5000/google-callback` (for development)
     - `http://gsale.levimylesllc.com/google-callback` (for production)
     - `https://gsale.levimylesllc.com/google-callback` (for production, if using HTTPS)
   - Click "Create"

5. Copy the Client ID and Client Secret

## Step 4: Configure Environment Variables

Create a `.env` file in your project root (or set environment variables):

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Flask Configuration
SECRET_KEY=your-secret-key-here

# Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_DB=gsale
```

## Step 5: Update Database Schema

Run the migration script to add Google OAuth support to your database:

```bash
mysql -u your_username -p your_database < sql/google_oauth_migration.sql
```

## Step 6: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Step 7: Test the Setup

1. Start your Flask application:
   ```bash
   python app.py
   ```

2. Navigate to `http://localhost:5000/login`
3. Click "Sign in with Google"
4. Complete the OAuth flow

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error**
   - Make sure the redirect URI in Google Cloud Console matches exactly
   - Include the full URL with protocol (http:// or https://)

2. **"Client ID not found" error**
   - Verify your GOOGLE_CLIENT_ID environment variable is set correctly
   - Check that the OAuth credentials are properly configured

3. **Database errors**
   - Ensure the migration script has been run
   - Check that the accounts table has the new columns

4. **"Invalid state parameter" error**
   - This is a security feature. Try refreshing the page and logging in again

5. **"Duplicate entry for key 'accounts.email'" error**
   - This happens when a user already exists with the same email
   - The system will automatically link the Google account to the existing user
   - If the linking fails, check that the database migration has been run

### Security Notes:

- Never commit your `.env` file to version control
- Use HTTPS in production
- Regularly rotate your client secret
- Monitor your OAuth usage in Google Cloud Console

## Production Deployment

For production deployment:

1. Use HTTPS (required by Google OAuth)
2. Update the authorized origins and redirect URIs in Google Cloud Console
3. Set proper environment variables on your server
4. Consider using a proper WSGI server like Gunicorn
5. Set up proper logging and monitoring

## Support

If you encounter issues:

1. Check the Flask application logs
2. Verify Google Cloud Console configuration
3. Test with a simple OAuth flow first
4. Ensure all environment variables are set correctly 