# Render Deployment Guide

## Steps to Deploy on Render

### 1. Prepare Your Repository
```bash
# Make sure everything is committed
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create Render Account & Setup
1. Go to [render.com](https://render.com)
2. Sign up / Log in with GitHub
3. Click **New +** → **Web Service**
4. Connect your GitHub repository

### 3. Configure the Web Service
- **Name**: `party-travel-planner` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`
- **Region**: Choose closest to your users
- **Plan**: Free tier works for testing

### 4. Add Environment Variables
Click **Environment** and add all these variables:

```
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_api_key>
GROQ_API_KEY=<your_groq_api_key>
RAPIDAPI_KEY=<your_rapidapi_key>
FOURSQUARE_API_KEY=<your_foursquare_api_key>
DEBUG=false
ENVIRONMENT=production
```

### 5. Deploy
Click **Create Web Service** and Render will automatically:
- Clone your repo
- Install dependencies
- Start your application
- Assign a live URL (e.g., `https://party-travel-planner.onrender.com`)

### 6. Verify Deployment
1. Visit your assigned URL
2. Test sign up / login
3. Create a test plan
4. Verify chatbot works

## Important Notes

### Security
✅ `.env` file is in `.gitignore` - never committed
✅ Environment variables stored securely in Render
✅ All API keys are private

### Database
✅ Supabase is cloud-hosted - works perfectly with Render
✅ No local database needed
✅ Access from any URL globally

### Performance
⚠️ Free tier may have startup delays (cold starts)
💡 Upgrade to **Starter** plan ($7/month) for better performance

### Auto-Deployment
Render automatically redeploys when you push to GitHub:
```bash
git push origin main  # Automatically deploys to Render
```

## Troubleshooting

### Port Binding Error
If you see port 8000 already in use:
- ✅ Code already fixed: uses `0.0.0.0:8000` for Render
- ✅ `host` set to `0.0.0.0` (not `127.0.0.1`)

### 500 Errors
1. Check Render logs: Dashboard → Services → party-travel-planner → Logs
2. Verify all environment variables are set
3. Verify Supabase credentials are correct

### Database Connection Issues
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` in environment
2. Test connection from Render logs
3. Ensure Supabase project is active

## Your Live URL
After deployment, share this URL:
```
https://party-travel-planner.onrender.com
```

Users can visit this to create travel plans and chat with the AI chatbot!
