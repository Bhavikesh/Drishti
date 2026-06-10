# 🚀 Drishti - Quick Start Guide

Get Drishti up and running in under 10 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Git installed
- 4GB RAM available
- Internet connection

## Step 1: Clone Repository

```bash
git clone https://github.com/your-org/drishti.git
cd drishti
```

## Step 2: Configure Environment

```bash
# Backend configuration
cp backend/.env.example backend/.env

# Frontend configuration  
cp frontend/.env.example frontend/.env
```

### Edit `backend/.env`:

```bash
# Minimum required configuration
MISTRAL_API_KEY=your_mistral_api_key_here
JWT_SECRET_KEY=your-secure-random-secret-change-this
```

**Get Mistral API Key:** Visit https://console.mistral.ai/

### Edit `frontend/.env`:

```bash
# Usually no changes needed for local development
VITE_API_URL=http://localhost:8000
```

## Step 3: Start Services

```bash
# Build and start all containers
docker-compose up -d

# Check logs
docker-compose logs -f
```

**Wait for services to start** (30-60 seconds)

## Step 4: Access Application

- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Step 5: Login

**Default Admin Credentials:**
- **Email:** admin@ksp.gov.in
- **Password:** Admin@123

⚠️ **Important:** Change the default password in production!

## That's It! 🎉

You now have Drishti running locally!

---

## Common Commands

### View Logs
```bash
docker-compose logs -f backend    # Backend logs
docker-compose logs -f frontend   # Frontend logs
docker-compose logs -f postgres   # Database logs
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Access Database
```bash
docker exec -it drishti-postgres psql -U drishti -d drishti
```

---

## Quick Testing

### Run Backend Tests
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov
pytest tests/ -v
```

### Test API Endpoints

**1. Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ksp.gov.in","password":"Admin@123"}'
```

**2. Chat Query (replace TOKEN with token from login):**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"message":"Show me crime statistics","session_id":"test","language":"en"}'
```

**3. Get Network Graph:**
```bash
curl -X POST http://localhost:8000/api/network/graph \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"crime_id":123}'
```

---

## Troubleshooting

### Services Won't Start

**Check Docker:**
```bash
docker --version
docker-compose --version
```

**Check ports:**
```bash
# Make sure ports 8000, 8080, 5432 are not in use
netstat -an | grep -E "8000|8080|5432"
```

### Database Connection Errors

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Frontend Not Loading

```bash
# Rebuild frontend
docker-compose up -d --build frontend
```

### "Network Error" in Browser

- Check if backend is running: http://localhost:8000
- Check browser console for CORS errors
- Verify VITE_API_URL in frontend/.env

---

## Next Steps

1. **Read Documentation:**
   - [README.md](README.md) - Full documentation
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Explore Features:**
   - Try chat queries
   - View network graphs
   - Generate forecasts
   - Export PDF reports

3. **Customize:**
   - Add your crime data
   - Configure users and roles
   - Customize UI branding
   - Setup monitoring

4. **Deploy to Production:**
   - Follow [DEPLOYMENT.md](DEPLOYMENT.md)
   - Setup SSL certificates
   - Configure backups
   - Train users

---

## Getting Help

- **Issues:** Create an issue in the repository
- **Documentation:** See [README.md](README.md)
- **API Reference:** http://localhost:8000/docs

---

**Happy Investigating! 🔍**
