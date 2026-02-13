# CITADEL KEBBI - Deployment Guide

Complete deployment options for CITADEL KEBBI Intelligence System.

---

## 🚀 Option 1: Free Deployment (Recommended for Demo)

### Backend - Render.com (FREE)
**Best for**: Python FastAPI backend

**Steps**:
1. Push code to GitHub
2. Go to https://render.com and sign up
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Runtime**: Python
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free ($0/month)

6. Add Environment Variables (copy from `.env`):
   - All API keys (GROQ, N2YO, NASA_FIRMS, etc.)

7. Click "Create Web Service"

**URL**: `https://your-app-name.onrender.com`

---

### Frontend - Vercel (FREE)
**Best for**: React/Vite frontend

**Steps**:
1. Go to https://vercel.com and sign up with GitHub
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variables:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   VITE_WS_URL=wss://your-backend.onrender.com
   ```

6. Click "Deploy"

**URL**: `https://your-app-name.vercel.app`

---

### Alternative Frontend - Netlify (FREE)
**Steps**:
1. Go to https://netlify.com
2. Drag & drop your `frontend/dist` folder after building locally
3. Or connect GitHub and set build settings same as Vercel

---

## 🚀 Option 2: Self-Hosted (Your Server)

### Requirements
- Ubuntu 20.04+ or Windows Server
- Python 3.10+
- Node.js 18+
- 2GB RAM minimum

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/citadel-kebbi.git
cd citadel-kebbi/backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp ../.env.example .env
# Edit .env with your API keys

# 5. Test
python -c "from main import app; print('OK')"

# 6. Run with systemd (Linux) or as service (Windows)
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Build

```bash
cd ../frontend

# 1. Install dependencies
npm install

# 2. Create production .env
echo "VITE_API_URL=http://your-server-ip:8000" > .env
echo "VITE_WS_URL=ws://your-server-ip:8000" >> .env

# 3. Build
npm run build

# 4. Serve dist/ folder with Nginx or copy to web server
```

### Nginx Configuration (Linux)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/citadel/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 🚀 Option 3: Docker Deployment

### Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

Deploy:
```bash
docker-compose up -d
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change default passwords in `.env`
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS (Cloudflare or Let's Encrypt)
- [ ] Restrict CORS origins in `main.py`
- [ ] Add rate limiting (configure in nginx or FastAPI)
- [ ] Enable WebSocket secure (wss://) for production

---

## 📊 Monitoring

### Free Monitoring Tools
- **Uptime**: https://uptimerobot.com (FREE - monitors every 5 min)
- **Logs**: Render/Netlify have built-in log viewers
- **Analytics**: Cloudflare (FREE tier)

---

## 💰 Cost Summary

| Service | Provider | Cost/Month |
|---------|----------|------------|
| Backend Hosting | Render | **$0** (Free tier) |
| Frontend Hosting | Vercel | **$0** (Free tier) |
| Domain | Namecheap | **$10/year** (optional) |
| SSL | Let's Encrypt | **$0** |
| CDN | Cloudflare | **$0** (Free tier) |
| **TOTAL** | | **$0/month** |

---

## 🆘 Troubleshooting

### Backend Won't Start
```bash
# Check Python version (need 3.10+)
python --version

# Check dependencies
pip list | grep fastapi

# Check .env file exists
ls -la backend/.env
```

### Frontend Can't Connect to Backend
1. Check `VITE_API_URL` matches backend URL
2. Ensure CORS is configured in `main.py`
3. Check browser console for errors

### API Rate Limits
- Check `/api/health/detailed` endpoint
- Review API key quotas
- Wait for daily resets (usually UTC midnight)

---

## 📞 Quick Deploy Commands

```bash
# One-command deploy (if you have Render/Vercel CLI)
render deploy  # Backend
vercel --prod  # Frontend
```

---

**Ready to deploy? Start with Render + Vercel for a completely FREE setup!**
