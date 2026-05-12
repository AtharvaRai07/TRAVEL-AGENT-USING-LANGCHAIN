# Pre-Deployment Checklist

## ✅ Code Changes Made

- [x] Updated `app/core/config.py` - Changed host to `0.0.0.0` for Render
- [x] Added CORS middleware to `app/main.py` for external access
- [x] Created `render.yaml` with deployment configuration
- [x] Created `.env.example` showing required environment variables
- [x] Updated `.gitignore` to exclude `.env` file

## 📋 Before Deploying to Render

### 1. Test Locally
```bash
cd c:\Users\mkuma\OneDrive\Desktop\PARTY
.venv\Scripts\python.exe main.py
```
Visit: http://127.0.0.1:8000

### 2. Commit Changes
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 3. Gather Your API Keys
You'll need these on Render dashboard:
- [ ] `SUPABASE_URL` - from Supabase project settings
- [ ] `SUPABASE_KEY` - from Supabase API keys
- [ ] `GROQ_API_KEY` - from Groq console
- [ ] `RAPIDAPI_KEY` - from RapidAPI dashboard
- [ ] `FOURSQUARE_API_KEY` - from Foursquare developer portal

## 🚀 Deploy to Render

### Step 1: Create Render Account
Visit: https://render.com
- Sign up with GitHub
- Authorize access to your repositories

### Step 2: Create Web Service
1. Click **New +** → **Web Service**
2. Select your repository
3. Fill in:
   - **Name**: `party-travel-planner`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Region**: Your preferred region
   - **Plan**: Free (or Starter for better performance)

### Step 3: Add Environment Variables
Click **Environment** and add:
```
SUPABASE_URL = (paste your value)
SUPABASE_KEY = (paste your value)
GROQ_API_KEY = (paste your value)
RAPIDAPI_KEY = (paste your value)
FOURSQUARE_API_KEY = (paste your value)
DEBUG = false
ENVIRONMENT = production
```

### Step 4: Deploy
Click **Create Web Service**
- Render will automatically deploy from `main` branch
- Wait 2-5 minutes for build to complete
- Your URL will be: `https://party-travel-planner.onrender.com`

## ✨ After Deployment

### Test Live App
1. Open your Render URL
2. Create an account with test email
3. Generate a travel plan
4. Test chatbot conversation
5. Create another plan to verify multiple plans display

### Monitor Logs
- Render Dashboard → Services → party-travel-planner → Logs
- Check for any errors

### Share Your App
Send this URL to users:
```
https://party-travel-planner.onrender.com
```

## 🔄 Future Deployments

After this, any code changes:
```bash
git push origin main  # Render auto-deploys
```

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| 500 error | Check environment variables in Render dashboard |
| App won't start | Check Render logs for missing dependencies |
| Database errors | Verify SUPABASE_URL and SUPABASE_KEY are correct |
| Cold start delays | Upgrade to Starter plan ($7/month) |
| Static files not loading | Ensure static files are in `app/static/` |

## 📞 Support

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/deployment/
- Supabase Docs: https://supabase.com/docs
