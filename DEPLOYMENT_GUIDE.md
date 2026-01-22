# 🚀 Elinity Games - Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] All lint errors resolved
- [x] Code committed to GitHub (commit: 2f28282)
- [x] Code pushed to origin/main
- [x] Deployment scripts ready
- [x] SSH access configured

---

## 📋 Deployment Options

### Option 1: SSH + Quick Deploy (Recommended)

**Step 1:** Connect to Hostinger VPS
```bash
# Using Windows PowerShell or Git Bash
ssh root@168.231.112.236
```

**Step 2:** Navigate to project directory
```bash
cd /root/elinity-backend-p1
```

**Step 3:** Run quick deployment script
```bash
bash quick_deploy.sh
```

This will:
- Pull latest code from GitHub
- Stop existing containers
- Rebuild and restart services
- Verify deployment

---

### Option 2: Manual Deployment

**Step 1:** SSH into server
```bash
ssh root@168.231.112.236
```

**Step 2:** Pull latest changes
```bash
cd /root/elinity-backend-p1
git pull origin main
```

**Step 3:** Restart Docker containers
```bash
sudo docker-compose down
sudo docker-compose up -d --build
```

**Step 4:** Monitor logs
```bash
sudo docker-compose logs -f elinity-app-final
```

---

### Option 3: Fresh Deployment (Clean Slate)

**Step 1:** SSH into server
```bash
ssh root@168.231.112.236
```

**Step 2:** Run Hostinger launch script
```bash
cd /root/elinity-backend-p1
bash hostinger_launch.sh
```

⚠️ **Warning:** This will wipe and restore the database from backup!

---

## 🧪 Post-Deployment Verification

### 1. Check Container Status
```bash
sudo docker-compose ps
```

Expected output:
```
NAME                    STATUS
elinity-app-final       Up
elinity-db-final        Up
elinity-redis-final     Up
```

### 2. Test API Endpoint
```bash
curl http://168.231.112.236:8090/docs
```

Or visit in browser: http://168.231.112.236:8090/docs

### 3. Test Game Endpoints

**Truth & Layer:**
```bash
curl -X POST http://168.231.112.236:8090/games/elinity-truth-and-layer/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_001", "ai_enabled": true}'
```

**Memory Mosaic:**
```bash
curl -X POST http://168.231.112.236:8090/games/elinity-memory-mosaic/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_001", "theme": "Childhood Dreams", "ai_enabled": true}'
```

**The Alignment Game:**
```bash
curl -X POST http://168.231.112.236:8090/games/elinity-the-alignment-game/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user_001", "ai_enabled": true}'
```

### 4. Check Logs for Errors
```bash
# Backend logs
sudo docker-compose logs -f elinity-app-final

# Database logs
sudo docker-compose logs -f elinity-db-final

# Redis logs
sudo docker-compose logs -f elinity-redis-final
```

---

## 🔧 Troubleshooting

### Issue: Containers won't start
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Try deployment again
sudo docker-compose up -d --build
```

### Issue: Port 8090 already in use
```bash
# Find process using port 8090
sudo lsof -i :8090

# Kill the process (replace PID)
sudo kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Issue: Database connection errors
```bash
# Check database is running
sudo docker exec -it elinity-db-final psql -U elinity_user -d elinity_db -c "SELECT 1;"

# If fails, restore from backup
cat ELINITY_FINAL_BACKUP.sql | sudo docker exec -i elinity-db-final psql -U elinity_user -d elinity_db
```

### Issue: Git pull fails
```bash
# Stash local changes
git stash

# Pull latest
git pull origin main

# Reapply changes if needed
git stash pop
```

---

## 📊 Monitoring Commands

### Real-time Logs
```bash
# All services
sudo docker-compose logs -f

# Specific service
sudo docker-compose logs -f elinity-app-final
```

### Resource Usage
```bash
# Container stats
sudo docker stats

# Disk usage
df -h

# Memory usage
free -h
```

### Database Queries
```bash
# Connect to database
sudo docker exec -it elinity-db-final psql -U elinity_user -d elinity_db

# Check game sessions
SELECT game_slug, COUNT(*) FROM game_sessions GROUP BY game_slug;

# Check users
SELECT COUNT(*) FROM users;
```

---

## 🔄 Rollback Procedure

If deployment fails:

**Step 1:** Revert to previous commit
```bash
git log --oneline -5  # Find previous commit hash
git checkout <previous-commit-hash>
```

**Step 2:** Rebuild containers
```bash
sudo docker-compose down
sudo docker-compose up -d --build
```

**Step 3:** Verify rollback
```bash
curl http://168.231.112.236:8090/docs
```

---

## 📝 Deployment Checklist

After deployment, verify:

- [ ] API docs accessible at http://168.231.112.236:8090/docs
- [ ] All 9 game endpoints respond correctly
- [ ] Database connections working
- [ ] Redis cache operational
- [ ] No errors in logs
- [ ] Frontend UI loads correctly
- [ ] Game stats display properly
- [ ] Shadow Observer integration working
- [ ] [UPDATE] tags being parsed
- [ ] Multiplayer sessions functional

---

## 🎯 Success Criteria

Deployment is successful when:

1. ✅ All containers running (3/3)
2. ✅ API responds with 200 status
3. ✅ Game start endpoints return valid session IDs
4. ✅ No critical errors in logs
5. ✅ Database queries execute successfully
6. ✅ Frontend UI renders without console errors

---

## 📞 Support

If issues persist:
1. Check `DEPLOYMENT_SUMMARY.md` for known issues
2. Review logs: `sudo docker-compose logs -f`
3. Verify environment variables in `.env`
4. Check Docker disk space: `df -h`
5. Restart all services: `sudo docker-compose restart`

---

**Last Updated:** January 22, 2026  
**Deployment Version:** 2f28282  
**Target Server:** Hostinger VPS (168.231.112.236:8090)
