# Deployment Guide

## Deploying JITU to Streamlit Cloud

### Prerequisites

1. GitHub account
2. Streamlit Cloud account (free at share.streamlit.io)

### Step-by-Step Deployment

#### 1. Prepare Your Repository

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - JITU application"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/jitu-app.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Set the following:
   - **Main file path**: `app.py`
   - **Python version**: 3.11
5. Click "Deploy"

#### 3. Configuration

The app will automatically use:
- `requirements.txt` for dependencies
- `.streamlit/config.toml` for theme settings

### Environment Variables

If you need to add secrets:

1. Go to your app settings in Streamlit Cloud
2. Add secrets in TOML format:

```toml
# .streamlit/secrets.toml (not committed to git)
[database]
username = "your_username"
password = "your_password"
```

### Custom Domain (Optional)

1. In Streamlit Cloud settings, go to "Custom domain"
2. Add your domain (e.g., jitu.yourdomain.com)
3. Update your DNS settings as instructed

## Alternative Deployment Options

### Deploy to Heroku

#### 1. Create Heroku Files

**Procfile:**
```
web: sh setup.sh && streamlit run app.py
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**runtime.txt:**
```
python-3.11.0
```

#### 2. Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create jitu-app

# Deploy
git push heroku main

# Open app
heroku open
```

### Deploy to AWS EC2

#### 1. Launch EC2 Instance

- AMI: Ubuntu 22.04 LTS
- Instance type: t2.micro (free tier)
- Security group: Allow ports 22, 80, 8501

#### 2. Connect and Setup

```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone repository
git clone https://github.com/yourusername/jitu-app.git
cd jitu-app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with screen (persistent session)
screen -S jitu
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Detach: Ctrl+A then D
# Reattach: screen -r jitu
```

#### 3. Setup Nginx (Optional, for production)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/jitu
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/jitu /etc/nginx/sites-enabled/

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Deploy to Google Cloud Run

#### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. Deploy

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jitu

# Deploy to Cloud Run
gcloud run deploy jitu \
  --image gcr.io/YOUR_PROJECT_ID/jitu \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

## Post-Deployment Checklist

- [ ] Test file upload functionality
- [ ] Verify all analytics calculations
- [ ] Check mobile responsiveness
- [ ] Test with sample data
- [ ] Monitor error logs
- [ ] Set up analytics (optional)
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate
- [ ] Enable auto-scaling if needed

## Monitoring

### Streamlit Cloud

Built-in monitoring at:
- App metrics: CPU, memory usage
- Logs: Real-time application logs
- Analytics: User activity

### Self-Hosted

Use tools like:
- **Uptime monitoring**: UptimeRobot, Pingdom
- **Application monitoring**: New Relic, Datadog
- **Log management**: Loggly, Papertrail

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

**Dependencies not installing:**
```bash
# Upgrade pip
pip install --upgrade pip

# Clear cache
pip cache purge
```

**Streamlit Cloud build fails:**
- Check Python version in requirements.txt
- Ensure all files are committed
- Check for syntax errors in code

## Maintenance

### Updates

```bash
# Pull latest changes
git pull origin main

# Restart application
# Streamlit Cloud: Auto-deploys on push
# Self-hosted: Restart streamlit process
```

### Backups

- Regular code backups via Git
- Export user data if applicable
- Database backups if using database

## Cost Estimates

### Streamlit Cloud
- **Free tier**: 1 app, unlimited viewers
- **Team**: $250/month for team features

### Heroku
- **Free tier**: Available but with limitations
- **Hobby**: $7/month per dyno

### AWS EC2
- **t2.micro**: Free tier for 12 months
- **After free tier**: ~$10/month

### Google Cloud Run
- **Pay per use**: ~$5-20/month for moderate traffic
