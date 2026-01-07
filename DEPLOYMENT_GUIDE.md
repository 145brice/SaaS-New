# Backend Deployment Guide for Render

## Overview
This guide shows how to deploy your Flask backend to Render so it can serve CSV files to your Next.js frontend.

## Prerequisites
- Render account (free tier available at https://render.com)
- GitHub repository with your backend code

## Backend Setup

### 1. Prepare Backend for Deployment

Your backend is already set up in: `c:\Users\user\OneDrive\Desktop\Permits Back End\SaaS-New\`

The `app_no_firebase.py` file now includes:
- `/api/leads` endpoint to serve CSV files
- CORS enabled for frontend communication
- Stripe validation (bypassed for test emails)

### 2. Create Requirements File

Create `requirements.txt` in your backend directory:

```txt
Flask==3.0.0
Flask-CORS==4.0.0
stripe==7.0.0
python-dotenv==1.0.0
```

### 3. Create Render Configuration

Create `render.yaml` in your backend directory:

```yaml
services:
  - type: web
    name: permits-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app_no_firebase.py
    envVars:
      - key: PORT
        value: 5002
      - key: FLASK_ENV
        value: production
```

### 4. Upload Leads Data to Backend

You need to copy your leads directory to your backend:

```
SaaS-New/
  leads/
    austin/
      2025-12-09/
        2025-12-09_austin.csv
    houston/
      2025-12-12/
        2025-12-12_houston.csv
    ...
```

### 5. Deploy to Render

1. **Create New Web Service**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - Name: `permits-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app_no_firebase.py`
   - Instance Type: `Free` (or paid for better performance)

3. **Environment Variables**
   Add these in Render dashboard:
   - `PORT`: `10000` (Render default)
   - `FLASK_ENV`: `production`
   - `STRIPE_SECRET_KEY`: Your Stripe secret key

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - You'll get a URL like: `https://permits-backend.onrender.com`

## Frontend Configuration

Update your frontend's `.env.local`:

```env
# Local development
BACKEND_URL=http://localhost:5002

# Production (update after deploying to Render)
# BACKEND_URL=https://permits-backend.onrender.com
```

For production deployment, update your Vercel/Netlify environment variables:
- Variable: `BACKEND_URL`
- Value: `https://permits-backend.onrender.com` (your actual Render URL)

## Testing

### Test Backend Locally (if Python is installed)

```bash
cd "c:\Users\user\OneDrive\Desktop\Permits Back End\SaaS-New"
python app_no_firebase.py
```

Then visit: http://localhost:5002/api/leads?city=austin&customer_id=145brice@gmail.com

### Test Frontend with Backend

1. Start your Next.js dev server
2. Go to your dashboard
3. Try downloading Austin leads
4. Frontend will call `/api/leads` → which proxies to backend → backend serves CSV

## Current Setup

✅ **Backend Updated**
- `/api/leads` endpoint created to serve CSV files
- Accepts `city` and `customer_id` parameters
- Returns CSV file as download
- Located at: [app_no_firebase.py](c:\Users\user\OneDrive\Desktop\Permits Back End\SaaS-New\app_no_firebase.py#L179-L219)

✅ **Frontend Updated**
- `/app/api/leads/route.ts` now proxies to backend
- Validates Stripe subscription first
- Fetches CSV from backend API
- Returns CSV to user
- Located at: [route.ts](c:\Users\user\OneDrive\Desktop\Fresh Repo Permits Clone\Permits-Front-End\app\api\leads\route.ts#L1-L82)

✅ **Environment Variables**
- `.env.local` created in frontend with `BACKEND_URL`

## Architecture Flow

```
User clicks "Download Austin" 
  → Frontend: /api/leads?city=austin&email=user@example.com
    → Validates Stripe subscription
    → Fetches: BACKEND_URL/api/leads?city=austin&customer_id=user@example.com
      → Backend: Finds CSV in leads/austin/latest/
      → Returns: CSV file
    → Frontend: Returns CSV to user as download
```

## Next Steps

1. **Deploy Backend to Render**
   - Follow steps above to deploy `app_no_firebase.py`
   - Copy leads data to backend deployment
   - Get your Render URL

2. **Update Frontend Environment**
   - Set `BACKEND_URL` in Vercel/Netlify environment variables
   - Redeploy frontend

3. **Test End-to-End**
   - Visit your live site
   - Try downloading leads for each city
   - Verify CSV downloads correctly

## Alternative: Keep Leads Local

If you want to keep serving CSVs from your frontend without a backend:

1. Don't deploy the backend
2. Revert the frontend changes to read local files
3. Keep the leads directory in your frontend repo
4. Deploy to Vercel/Netlify with the leads folder

**Pros**: Simpler, no backend needed
**Cons**: Leads are public in your repo, harder to update dynamically

## Troubleshooting

**Backend can't find CSV files**
- Ensure leads directory is in the correct location relative to `app_no_firebase.py`
- Update the path in line 195 of `app_no_firebase.py`

**CORS errors**
- Backend already has CORS enabled with `Flask-CORS`
- If issues persist, update CORS config to whitelist your frontend domain

**Stripe validation failing**
- Test with `145brice@gmail.com` which bypasses validation
- Ensure your Stripe secret key is set in environment variables
