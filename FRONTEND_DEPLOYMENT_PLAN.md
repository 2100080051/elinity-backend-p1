# 🎮 Elinity Games Frontend Deployment Plan

## 📊 Current Situation

### **Two Types of Games:**

1. **Premium 10 Games** (in `elinity-backend-github/game-ui`)
   - These use the NEW premium UI/UX we just enhanced
   - Built with React + Vite
   - Single unified frontend application
   - Connected to backend at port 8090

2. **Legacy 58 Games** (in `elinity game suite/`)
   - Individual Next.js applications
   - Previously deployed to Azure
   - Each game is a separate deployment

---

## 🚀 DEPLOYMENT STRATEGY

### **OPTION 1: Deploy Premium 10 Games (Recommended First)**

These are the games we just enhanced with premium UI:
1. Truth & Layer
2. Memory Mosaic
3. The Alignment Game
4. The Compass Game
5. Myth Maker Arena
6. Echoes & Expressions
7. The Long Quest
8. The Story Weaver
9. World Builders
10. Serendipity Strings

#### **Steps:**

**A. Build the Frontend**
```bash
cd c:\Users\nabhi\Downloads\python_elinity-main2\elinity-backend-github\game-ui
npm install
npm run build
```

**B. Deploy Options:**

**Option B1: Static Hosting (Vercel/Netlify) - EASIEST**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd c:\Users\nabhi\Downloads\python_elinity-main2\elinity-backend-github\game-ui
vercel --prod
```

**Option B2: Azure Static Web Apps**
```bash
# Using Azure CLI
az staticwebapp create \
  --name elinity-premium-games \
  --resource-group elinity-rg \
  --source c:\Users\nabhi\Downloads\python_elinity-main2\elinity-backend-github\game-ui \
  --location "East US" \
  --branch main \
  --app-location "/" \
  --output-location "dist"
```

**Option B3: Hostinger (if SSH works)**
```bash
# Build locally
npm run build

# Upload dist folder to Hostinger
scp -r dist/* root@168.231.112.236:/var/www/elinity-games/

# Configure Nginx to serve static files
```

---

### **OPTION 2: Deploy Legacy 58 Games**

These are the individual Next.js games in "elinity game suite" folder.

#### **Previous Deployment Method (Azure):**

You had a script: `master_deploy.js` that deployed all 58 games to Azure App Services.

**Check if it still works:**
```bash
cd "c:\Users\nabhi\Downloads\python_elinity-main2\elinity game suite"
node master_deploy.js
```

#### **Alternative: Mass Deploy to Vercel**

Create a script to deploy all 58 games:

```javascript
// deploy_all_games.js
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const gamesDir = './';
const games = fs.readdirSync(gamesDir)
  .filter(f => f.startsWith('elinity-') && fs.statSync(path.join(gamesDir, f)).isDirectory());

console.log(`Found ${games.length} games to deploy`);

games.forEach((game, index) => {
  console.log(`\n[${index + 1}/${games.length}] Deploying ${game}...`);
  try {
    process.chdir(path.join(gamesDir, game));
    execSync('vercel --prod', { stdio: 'inherit' });
    console.log(`✅ ${game} deployed successfully`);
  } catch (error) {
    console.error(`❌ ${game} failed:`, error.message);
  }
});
```

---

## 🎯 RECOMMENDED DEPLOYMENT ORDER

### **Phase 1: Premium 10 Games (Priority)**
1. Build the unified game-ui frontend
2. Deploy to Vercel (fastest, free tier available)
3. Update backend CORS to allow Vercel domain
4. Test all 10 games

### **Phase 2: Legacy 58 Games (If Needed)**
1. Check if Azure deployments still work
2. If not, migrate to Vercel/Netlify
3. Update backend to handle all game endpoints

---

## 📝 DETAILED STEPS FOR PREMIUM 10 GAMES

### **Step 1: Prepare Frontend**

```bash
cd c:\Users\nabhi\Downloads\python_elinity-main2\elinity-backend-github\game-ui

# Install dependencies
npm install

# Create production build
npm run build
```

### **Step 2: Deploy to Vercel (Recommended)**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Follow prompts:
# - Project name: elinity-premium-games
# - Framework: Vite
# - Build command: npm run build
# - Output directory: dist
```

### **Step 3: Update Backend CORS**

In `elinity-backend-github/main.py`, update CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://elinity-premium-games.vercel.app",  # Production
        "https://*.vercel.app"  # All Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Step 4: Update Frontend API URL**

In `game-ui/src/api/client.ts` or config:

```typescript
const API_BASE_URL = import.meta.env.PROD 
  ? 'http://168.231.112.236:8090'  // Production backend
  : 'http://localhost:8081';        // Local backend
```

### **Step 5: Test Deployment**

Visit: `https://elinity-premium-games.vercel.app`

Test each game:
- Truth & Layer
- Memory Mosaic
- The Alignment Game
- etc.

---

## 🔧 ENVIRONMENT VARIABLES

Create `.env.production` in game-ui folder:

```env
VITE_API_URL=http://168.231.112.236:8090
VITE_WS_URL=ws://168.231.112.236:8090
```

---

## 📊 DEPLOYMENT COMPARISON

| Method | Cost | Speed | Ease | SSL | CDN |
|--------|------|-------|------|-----|-----|
| **Vercel** | Free tier | ⚡ Fast | ✅ Easy | ✅ Auto | ✅ Yes |
| **Netlify** | Free tier | ⚡ Fast | ✅ Easy | ✅ Auto | ✅ Yes |
| **Azure Static** | ~$10/mo | 🐢 Slow | ⚠️ Medium | ✅ Auto | ✅ Yes |
| **Hostinger** | Included | 🐢 Slow | ❌ Hard | ⚠️ Manual | ❌ No |

**Recommendation: Use Vercel for fastest deployment**

---

## 🚨 IMPORTANT NOTES

1. **Backend Must Be Running**
   - Premium games need backend at `http://168.231.112.236:8090`
   - Make sure Hostinger backend is deployed first

2. **CORS Configuration**
   - Update backend to allow frontend domain
   - Test with browser console for CORS errors

3. **WebSocket Support**
   - Some games use WebSockets for multiplayer
   - Ensure WS connections are allowed

4. **API Keys**
   - Don't expose OpenRouter API key in frontend
   - All AI calls should go through backend

---

## ✅ QUICK START (Premium 10 Games)

```bash
# 1. Navigate to game-ui
cd c:\Users\nabhi\Downloads\python_elinity-main2\elinity-backend-github\game-ui

# 2. Install Vercel CLI
npm install -g vercel

# 3. Build and deploy
npm run build
vercel --prod

# 4. Done! You'll get a URL like:
# https://elinity-premium-games.vercel.app
```

---

## 📞 Next Steps

1. **Deploy Premium 10 Games to Vercel** (15 minutes)
2. **Update backend CORS** (5 minutes)
3. **Test all games** (30 minutes)
4. **Deploy Legacy 58 Games** (if needed, 2-3 hours)

**Which would you like to start with?**
