# Backend-Frontend Integration

## Summary

Your backend and frontend are now connected! Here's how it works:

## Architecture

```
User → Frontend (Next.js) → Frontend API Route → Backend API (Flask) → CSV Files
```

### Flow:
1. User goes to dashboard and clicks "Download Austin"
2. Frontend calls `/api/leads?city=austin&email=user@example.com`
3. Frontend API validates Stripe subscription
4. Frontend API proxies request to backend: `BACKEND_URL/api/leads?city=austin`
5. Backend finds the latest CSV file for Austin
6. Backend returns CSV to frontend
7. Frontend returns CSV to user as download

## Files Changed

### Backend: `app_no_firebase.py`
- **New endpoint**: `/api/leads` - Serves CSV files
- **Location**: Lines 179-232
- **What it does**: 
  - Accepts `city` and `customer_id` parameters
  - Finds the most recent CSV file for that city
  - Returns the CSV file as a download
  - Works with both local (development) and deployed (production) paths

### Frontend: `app/api/leads/route.ts`  
- **Updated**: Now proxies to backend instead of reading local files
- **What it does**:
  - Validates user has active Stripe subscription
  - Calls backend API to get CSV
  - Returns CSV to user

### Frontend: `.env.local`
- **New**: Environment variable for backend URL
- **Value**: `BACKEND_URL=http://localhost:5002` (local dev)
- **Production**: Update to your Render URL

## Local Development

Since Python isn't detected on your system, you have 2 options:

### Option 1: Use Frontend-Only (Easiest for now)
The frontend can still work by reading local CSV files. Just revert the changes:

```bash
# In your frontend directory
git checkout app/api/leads/route.ts
```

This will make it read from `leads/austin/2025-12-09/` again.

### Option 2: Deploy Backend to Render (Recommended for production)

1. **Push backend to GitHub**
   ```bash
   cd "c:\Users\user\OneDrive\Desktop\Permits Back End\SaaS-New"
   git init
   git add .
   git commit -m "Initial backend commit"
   git remote add origin YOUR_GITHUB_REPO
   git push -u origin main
   ```

2. **Deploy to Render**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your backend GitHub repo
   - Render will auto-detect `render.yaml` and configure everything
   - Click "Create Web Service"

3. **Copy Leads Data**
   Create a `leads/` directory in your backend with the same structure:
   ```
   SaaS-New/
     leads/
       austin/
         2025-12-09/
           2025-12-09_austin.csv
       houston/
         2025-12-12/
           2025-12-12_houston.csv
   ```

4. **Update Frontend**
   In Vercel/Netlify environment variables:
   - Add: `BACKEND_URL` = `https://your-app.onrender.com`
   - Redeploy frontend

## Testing

### Test Backend Endpoint (when deployed)
```
https://your-app.onrender.com/api/leads?city=austin&customer_id=145brice@gmail.com
```

Should download: `2025-12-09_austin.csv`

### Test Frontend
1. Go to your dashboard
2. Click "Download Austin"  
3. Should download CSV file

## Current Status

✅ Backend code ready (`app_no_firebase.py`)
✅ Frontend code updated to use backend
✅ Environment variables configured
✅ Deployment config created (`render.yaml`)

⏳ Pending: Deploy backend to Render
⏳ Pending: Copy leads data to backend
⏳ Pending: Update frontend env vars with Render URL

## Quick Commands

### Start Backend Locally (if Python works):
```bash
cd "c:\Users\user\OneDrive\Desktop\Permits Back End\SaaS-New"
python app_no_firebase.py
```

### Test API:
```bash
curl "http://localhost:5002/api/leads?city=austin&customer_id=145brice@gmail.com"
```

### Build Frontend:
```bash
cd "c:\Users\user\OneDrive\Desktop\Fresh Repo Permits Clone\Permits-Front-End"
npm run build
```

## Troubleshooting

**Backend can't find CSV files**
- Check that `leads/` directory exists in backend
- Check that city name matches (lowercase: `austin` not `Austin`)

**Frontend shows error**
- Check `BACKEND_URL` is set correctly
- Make sure backend is running
- Check browser console for CORS errors

**CORS errors**
- Backend has `Flask-CORS` enabled
- Should work out of the box
- If issues, add your frontend domain to CORS config

## Next Steps

1. Deploy backend to Render
2. Get Render URL (e.g., `https://permits-backend-api.onrender.com`)
3. Update frontend `.env.local` and Vercel/Netlify env vars
4. Test end-to-end

Or stick with frontend-only approach for now and deploy backend later!
