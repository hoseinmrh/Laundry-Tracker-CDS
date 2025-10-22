# Deployment Guide for Render.com

## Prerequisites
- GitHub account
- Render.com account (free)
- Your Telegram Bot Token from @BotFather

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
# Initialize git if you haven't already
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Laundry Tracker Bot"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/laundry-tracker.git
git branch -M main
git push -u origin main
```

### 2. Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your GitHub account (recommended)

### 3. Create a New Background Worker

1. From your Render dashboard, click **"New +"** button
2. Select **"Background Worker"**
3. Connect your GitHub repository:
   - If first time: Click "Connect GitHub" and authorize Render
   - Select your `laundry-tracker` repository
4. Configure the service:
   - **Name**: `laundry-tracker-bot` (or any name you prefer)
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt` (auto-detected)
   - **Start Command**: `python bot.py` (auto-detected from Procfile)

### 4. Add Environment Variables

1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"**
3. Add:
   - **Key**: `BOT_TOKEN`
   - **Value**: Your bot token from @BotFather (paste it here)

### 5. Deploy!

1. Scroll to the bottom and click **"Create Background Worker"**
2. Render will now:
   - Clone your repository
   - Install dependencies
   - Start your bot
3. Watch the logs to confirm it's working - you should see:
   ```
   🤖 Bot is starting...
   ✅ Bot is running! Press Ctrl+C to stop.
   ```

### 6. Test Your Bot

1. Open Telegram
2. Search for your bot
3. Send `/start`
4. Try all the features!

## Important Notes

### CSV File Persistence

⚠️ **Important**: Render's free tier doesn't have persistent storage. This means:
- CSV files will be recreated on each deployment/restart
- All data (machine status, users) will be lost on restart

### Solutions:

**Option 1: Quick Fix - Add a Persistent Disk (Free)**
1. In your Render service, go to "Disks"
2. Add a disk with mount path: `/app/data`
3. Update file paths in `data_manager.py` to use `/app/data/` prefix

**Option 2: Upgrade to Database (Recommended for production)**
- Use Render's free PostgreSQL database
- I can help you migrate from CSV to PostgreSQL later

**Option 3: Use Render Persistent Disk**
- Free tier includes 1GB persistent disk
- Mount it to your service

For now, the bot will work fine for testing. Data resets only happen on:
- Manual deploys
- Service restarts (rare)
- Code changes pushed to GitHub

## Monitoring Your Bot

### View Logs
1. Go to your service dashboard on Render
2. Click on "Logs" tab
3. See real-time bot activity

### Auto-Deploy on Git Push
Render automatically redeploys when you push to your `main` branch:

```bash
git add .
git commit -m "Update bot features"
git push
```

## Troubleshooting

### Bot not responding
- Check logs on Render dashboard
- Verify `BOT_TOKEN` is set correctly
- Ensure service status is "Live" (green)

### Import errors
- Check that `requirements.txt` includes all dependencies
- View build logs to see if installation succeeded

### Service keeps restarting
- Check for Python errors in logs
- Verify `bot.py` runs without errors locally first

## Free Tier Limits

Render free tier includes:
- ✅ 750 hours/month (enough for 24/7 operation)
- ✅ Background worker support
- ✅ Auto-deploy from GitHub
- ✅ Environment variables
- ✅ 1GB persistent disk (optional)

## Stopping the Bot

To stop your bot:
1. Go to your service dashboard
2. Click "Suspend" to pause (can resume anytime)
3. Or delete the service entirely

## Need Help?

If you run into issues:
1. Check the Render logs first
2. Verify all environment variables are set
3. Test the bot locally before deploying
4. Check Render's status page: status.render.com

---

**Your bot is now live 24/7! 🎉**
