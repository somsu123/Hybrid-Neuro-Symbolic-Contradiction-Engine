# 🚀 Quick Deployment Guide

## Deploy to Render in 5 Minutes

### Step 1: Prepare Your Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Add Render deployment configuration"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to **[Render Dashboard](https://dashboard.render.com/)**
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub repository**
4. Render will auto-detect the `render.yaml` configuration
5. Click **"Create Web Service"**

That's it! Render will:
- Install all dependencies
- Download the spaCy model
- Start your application
- Provide you with a live URL

### Step 3: Test Your Deployment

Once deployed, visit:
- **Web Interface:** `https://your-app-name.onrender.com`
- **Health Check:** `https://your-app-name.onrender.com/api/health`

---

## Manual Configuration (if needed)

If Render doesn't auto-detect `render.yaml`:

### Service Settings:
- **Name:** `contradiction-engine`
- **Environment:** `Python 3`
- **Region:** Choose closest to you
- **Branch:** `main`

### Build & Deploy:
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python -m spacy download en_core_web_sm
  ```

- **Start Command:**
  ```bash
  gunicorn app:app
  ```

### Advanced Settings:
- **Health Check Path:** `/api/health`
- **Auto-Deploy:** `Yes` (redeploys on git push)

---

## Local Testing Before Deploy

Test locally to ensure everything works:

```bash
# Activate virtual environment (if using)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the application
python app.py

# Open browser
# Navigate to: http://localhost:5000
```

---

## API Endpoints

### POST /api/detect
Detect contradictions in text:

**Using File Upload:**
```bash
curl -X POST https://your-app.onrender.com/api/detect \
  -F "file=@sample.txt" \
  -F "threshold=0.5"
```

**Using JSON:**
```bash
curl -X POST https://your-app.onrender.com/api/detect \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your narrative text here...",
    "threshold": 0.5
  }'
```

### GET /api/health
Check if service is running:
```bash
curl https://your-app.onrender.com/api/health
```

### GET /api/sample
Get sample text for testing:
```bash
curl https://your-app.onrender.com/api/sample
```

---

## Important Notes

### Free Tier Limitations:
- ⏱️ **Cold Start:** Service sleeps after 15 minutes of inactivity
- 🐌 **Wake Time:** First request after sleep takes 30-60 seconds
- 💾 **Memory:** 512MB limit (sufficient for simplified mode)

### Performance Tips:
- The web app uses **simplified mode** by default (fast, no heavy models)
- First analysis will be slower (model initialization)
- Subsequent analyses are much faster (models cached)

### Upgrading:
For production use, consider:
- **Paid Tier:** No cold starts, more memory
- **Custom Domain:** Add your own domain
- **Environment Variables:** Store API keys securely

---

## Troubleshooting

### Build Fails:
- Check `requirements.txt` syntax
- Ensure all dependencies are compatible
- Review Render build logs

### App Doesn't Start:
- Verify `gunicorn` is in requirements.txt
- Check `app.py` has no syntax errors
- Review Render runtime logs

### Health Check Fails:
- Ensure Flask app is listening on `0.0.0.0`
- Verify `/api/health` endpoint returns JSON
- Check PORT environment variable is used

### Upload Fails:
- Ensure file is `.txt` format
- Check file size < 5MB
- Verify text is UTF-8 encoded

---

## Next Steps

✅ **Your app is now live!**

Share your deployed app:
- Send the URL to others to test
- Upload different text samples
- Adjust threshold to see different results

For full documentation, see:
- [README.md](README.md)
- [Walkthrough](C:\Users\somsubhro\.gemini\antigravity\brain\19613cd6-2a69-476f-8448-65b16c346be6\walkthrough.md)
