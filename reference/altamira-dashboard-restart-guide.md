# Altamira Dashboard — Restart Guide

## Quick Reference

| Component | Technology | Port | Location |
|-----------|-----------|------|----------|
| Dashboard (UI) | Next.js 15 (Turbopack) | **3001** | `C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone` |
| Database | MongoDB 7 (Docker) | **27017** | Docker container named `mongodb` |

**URL:** http://localhost:3001

---

## Quick Restart (Copy-Paste)

Open a terminal (Git Bash, PowerShell, or CMD) and run:

### Git Bash / WSL

```bash
# 1. Start Docker Desktop (skip if already running)
"/c/Program Files/Docker/Docker/Docker Desktop.exe" &
# Wait ~30 seconds for Docker to initialize

# 2. Start MongoDB
docker start mongodb

# 3. Kill any stale Next.js process on port 3001
for pid in $(netstat -ano | grep "3001" | grep LISTENING | awk '{print $5}' | sort -u); do
  taskkill //PID $pid //F
done

# 4. Start the dashboard
cd "C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone"
npx next dev --turbopack -p 3001
```

### PowerShell

```powershell
# 1. Start Docker Desktop (skip if already running)
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# Wait ~30 seconds for Docker to initialize

# 2. Start MongoDB
docker start mongodb

# 3. Kill any stale Next.js process on port 3001
Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

# 4. Start the dashboard
Set-Location "C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone"
npx next dev --turbopack -p 3001
```

---

## Step-by-Step Walkthrough

### Step 1: Check if the dashboard is already running

Open http://localhost:3001 in your browser. If it loads (or redirects to a login page), you're done.

### Step 2: Start Docker Desktop

The dashboard needs MongoDB, which runs in Docker.

- **Check:** Open a terminal and run `docker ps`. If it returns results, Docker is running.
- **If not running:** Launch Docker Desktop from the Start menu or taskbar. Wait until the Docker icon in the system tray shows "running" (usually 20-40 seconds).

### Step 3: Start MongoDB

```bash
docker start mongodb
```

**Verify:** Run `docker ps --filter "name=mongodb"` — you should see status `Up ... (healthy)`.

**If the container doesn't exist** (e.g., after a Docker reset):

```bash
cd "C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone"
docker compose up -d mongodb
```

### Step 4: Kill stale processes on port 3001

Sometimes a previous Next.js process hangs. Check and kill it:

```bash
# Check what's on port 3001
netstat -ano | findstr "3001" | findstr LISTENING

# If you see a PID, kill it
taskkill /PID <PID_NUMBER> /F
```

### Step 5: Start the Next.js app

```bash
cd "C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone"
npx next dev --turbopack -p 3001
```

The terminal will show:

```
   ▲ Next.js 15.x.x (Turbopack)
   - Local:   http://localhost:3001
```

### Step 6: Verify

Open http://localhost:3001 in your browser. You should see the dashboard (or a login/auth redirect).

---

## Troubleshooting

### "Port 3001 is already in use"

A stale Node process is hogging the port. Kill it first (Step 4 above).

### "MongoServerError: connect ECONNREFUSED"

MongoDB isn't running. Go back to Step 2 and Step 3.

### "Docker daemon not running"

Docker Desktop isn't started. Launch it from the Start menu and wait for it to fully initialize.

### Dashboard loads but shows errors / blank page

1. Check the terminal where `next dev` is running for error messages.
2. Make sure `.env` exists in the project root with the correct MongoDB URI:
   ```
   MONGODB_URI=mongodb://root:example@localhost:27017/openstock?authSource=admin
   BETTER_AUTH_SECRET=<your-secret>
   BETTER_AUTH_URL=http://localhost:3001
   ```
3. Try stopping and restarting: `Ctrl+C` in the terminal, then re-run the `npx next dev` command.

### MongoDB container was removed

Recreate it:

```bash
cd "C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone"
docker compose up -d mongodb
```

This creates a fresh container. The `mongo-data` Docker volume preserves your data across container recreations.

---

## Architecture Notes

- **Next.js** runs in dev mode with Turbopack for fast HMR. Port 3001 is explicitly set (default would be 3000).
- **MongoDB** runs in a Docker container with persistent volume (`mongo-data`). Credentials: `root` / `example`.
- **Auth** uses better-auth, which is why the root URL redirects (307) to a login page.
- The Docker `docker-compose.yml` also defines an `openstock` service for production builds, but for development you only need the `mongodb` service running in Docker + `next dev` on the host.
