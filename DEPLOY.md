# Deploy THE VACHAS for public use

This guide gets the platform online so **anyone can visit the public site** and **members can log in**.

## What you need before deploying

| Item | Why |
|------|-----|
| **Domain name** (optional but recommended) | e.g. `thevachas.org` — looks professional |
| **PostgreSQL database** | Production must NOT use SQLite |
| **Hosting account** | Server or PaaS to run the app |
| **SECRET_KEY** | Random string for Django security |

You do **not** need SQLite installed. Production uses **PostgreSQL only**.

---

## Step 1 — Generate a secret key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output into your production `.env` as `SECRET_KEY=...`

---

## Step 2 — Create production `.env`

```bash
copy .env.production.example .env
```

Edit `.env` and set:

```env
SECRET_KEY=your-generated-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

DB_NAME=vachas
DB_USER=vachas
DB_PASSWORD=your-strong-db-password
DB_HOST=db
DB_PORT=5432

RUN_SEED=true
```

Replace `yourdomain.com` with your real domain (or your host's URL like `vachas.onrender.com`).

---

## Option A — Deploy with Docker (VPS: DigitalOcean, Hetzner, AWS EC2)

Best if you want full control and persistent file uploads (photos, publications).

### On your server (Ubuntu)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Clone your project
git clone <your-repo-url> vachas
cd vachas

# Configure environment
cp .env.production.example .env
nano .env   # fill in values

# Build and start
docker compose -f docker-compose.prod.yml up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f web
```

Site will be at: `http://YOUR_SERVER_IP:8000`

### Add HTTPS (recommended)

1. Point your domain A record → server IP
2. Install Caddy or Nginx + Certbot as reverse proxy
3. Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to your HTTPS domain

---

## Option B — Deploy on Render (easier, good for portfolio)

1. Push code to **GitHub**
2. Go to [render.com](https://render.com) → New **Web Service**
3. Connect your repo
4. Settings:
   - **Environment:** Docker
   - **Dockerfile path:** `Dockerfile`
   - **Instance type:** Free or Starter

5. Add **PostgreSQL** database on Render (New → PostgreSQL)

6. Environment variables on the Web Service:

| Key | Value |
|-----|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | (generated key) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` |
| `DATABASE_URL` | (paste from Render PostgreSQL dashboard) |
| `RUN_SEED` | `true` (first deploy only, then set `false`) |

7. Deploy → visit `https://your-app.onrender.com`

**Note:** On free Render, uploaded media may not persist after redeploys. For heavy gallery/uploads, use Option A or add cloud storage (S3) later.

---

## Option C — Railway

Similar to Render:

1. Push to GitHub
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add PostgreSQL plugin
4. Set env vars (same as Render table above)
5. Railway auto-sets `DATABASE_URL`

---

## After first deploy

### Default accounts (if `RUN_SEED=true`)

| Username | Password | Role |
|----------|----------|------|
| developer | devpass123 | Developer |
| lead | leadpass123 | Lead |
| core | corepass123 | Core Team |
| member | memberpass123 | Member |

**Change these passwords immediately** in production:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py changepassword developer
```

Or via Django admin: `/admin/` (log in as `developer` — has `is_staff`).

### Create Django superuser (optional)

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## Production checklist

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `CSRF_TRUSTED_ORIGINS` includes `https://yourdomain.com`
- [ ] PostgreSQL connected (not SQLite)
- [ ] Default seed passwords changed
- [ ] HTTPS enabled
- [ ] `RUN_SEED=false` after first deploy

---

## Local dev vs production

| | Local (your laptop) | Production (public) |
|--|---------------------|---------------------|
| Database | SQLite (automatic) | PostgreSQL (required) |
| DEBUG | True | False |
| Who can access | Only you | Everyone on the internet |

---

## Need help choosing?

Tell me:
1. Do you have a **domain name**?
2. Budget: **free** / **low cost (~$5/mo)** / **VPS**?
3. Do you have a **GitHub repo** for this project?

I can walk you through the exact clicks for your chosen platform.
