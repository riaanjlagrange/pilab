# Homelab

Self-hosted media and home automation stack running on a Raspberry Pi 4B.
Fully containerised with Docker. Accessible via a custom domain with SSL.

---

## Stack

| Container | Purpose | URL |
|---|---|---|
| **Plex** | Media streaming | `plex.rpi.{DOMAIN}` |
| **Seerr** | Media requests & discovery | `seerr.rpi.{DOMAIN}` |
| **Radarr** | Automated movie downloads | `radarr.rpi.{DOMAIN}` |
| **Sonarr** | Automated series downloads | `sonarr.rpi.{DOMAIN}` |
| **Prowlarr** | Torrent indexer manager | `prowlarr.rpi.{DOMAIN}` |
| **qBittorrent** | Torrent download client | `qbittorrent.rpi.{DOMAIN}` |
| **Pi-hole** | Network-wide ad blocking | `pihole.rpi.{DOMAIN}/admin` |
| **Nginx Proxy Manager** | Reverse proxy + SSL | `rpi.local:81` |
| **Wetty** | Browser-based SSH | `ssh.rpi.{DOMAIN}` |
| **Glances** | System monitoring | `glances.rpi.{DOMAIN}` |
| **Dozzle** | Live container logs | `dozzle.rpi.{DOMAIN}` |
| **Watchtower** | Auto container updates | — |
| **File Browser** | File management UI | `files.rpi.{DOMAIN}` |
| **homelab-api** | Central Flask API | `api.rpi.{DOMAIN}` |
| **homelab-dashboard** | Dynamic homelab dashboard | `rpi.{DOMAIN}` |
| **homelab-storage** | Storage manager UI | `storage.rpi.{DOMAIN}` |
| **wg-easy** | VPN | `vpn.rpi.{DOMAIN}` |

---

## Architecture

```
~/homelab/
├── containers/
│   ├── api/                ← Flask backend (central API for all UIs)
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── dashboard/          ← Dynamic dashboard (nginx, talks to API)
│   │   └── index.html
│   ├── storage-manager/    ← Storage manager UI (nginx, talks to API)
│   │   └── index.html
│   ├── radarr/config/      ← App data (gitignored)
│   ├── sonarr/config/      ← App data (gitignored)
│   └── ...
├── media/                  ← Movies, series, downloads (gitignored)
├── shared/                 ← SMB shared files
│   └── index.html
├── docker-compose.yml
├── .env                    ← Real secrets (gitignored — copy from .env.example)
└── .env.example            ← Template — fill this in on a fresh install
```

The `homelab-api` container is the single backend for the entire stack:
- `/api/system` - hostname, CPU, RAM, uptime (via Glances)
- `/api/disk` - free/used/total GB
- `/api/containers` — all Docker containers with status + uptime
- `/api/plex` - active sessions + on-deck (continue watching)
- `/api/media` - movies + series from Radarr/Sonarr
- `/api/delete` - delete media via Radarr/Sonarr API (removes files too)
- `/api/camera/status` - status of rpi cam
- `/api/camera/stream` - livestream of rpi cam feed
- `/api/camera/snapshot` - snapshot from rpi cam
---

## Fresh Install

### 1. Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Install Git
sudo apt install -y git
```

### 2. Clone the repo

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/homelab.git
cd homelab
```

### 3. Create your .env file

```bash
cp .env.example .env
nano .env
```

Fill in every value. See `.env.example` for descriptions.

### 4. Create required directories

These are gitignored (app data + media) so they won't exist after a fresh clone:

```bash
# Container config dirs
mkdir -p containers/radarr/config
mkdir -p containers/sonarr/config
mkdir -p containers/prowlarr/config
mkdir -p containers/seerr/config
mkdir -p containers/qbittorrent/config
mkdir -p containers/plex/config containers/plex/transcode
mkdir -p containers/pihole/etc-pihole containers/pihole/etc-dnsmasq.d
mkdir -p containers/nginxproxymanager/data containers/nginxproxymanager/letsencrypt
mkdir -p containers/filebrowser
mkdir -p containers/wg-easy
mkdir -p containers/camera

# Media dirs
mkdir -p media/movies media/series media/downloads/incomplete

# Shared
mkdir -p shared
```

### 5. Build and start

```bash
docker compose up -d
```

Watch logs:
```bash
docker compose logs -f
```

### 6. First-time setup (manual steps)

These can't be automated — they need the apps to be running first:

| Step | Where |
|---|---|
| Get Radarr API key | Radarr → Settings → General → Security |
| Get Sonarr API key | Sonarr → Settings → General → Security |
| Get Prowlarr API key | Prowlarr → Settings → General → Security |
| Get Seerr API key | Seerr → Settings → General |
| Configure Radarr/Sonarr in Seerr | Seerr → Settings → Radarr / Sonarr |
| Add indexers in Prowlarr | Prowlarr → Indexers |
| Sync Prowlarr to Radarr/Sonarr | Prowlarr → Settings → Apps |
| Add NPM proxy hosts | `rpi.local:81` → Proxy Hosts |
| Add DNS records | Cloudflare → DNS |
| Get Plex token | `cat containers/plex/config/.../Preferences.xml \| grep PlexOnlineToken` |
| Add Plex token to .env | `nano .env` → restart homelab-api |

### 7. Nginx Proxy Manager

All subdomains follow the pattern `{container}.rpi.{DOMAIN}` except:
- Dashboard → `rpi.{DOMAIN}` → forward to `homelab-dashboard:80`
- Storage → `storage.rpi.{DOMAIN}` → forward to `homelab-storage:80`
- API → `api.rpi.{DOMAIN}` → forward to `homelab-api:5000`
- SSH → `ssh.rpi.{DOMAIN}` → forward to `wetty:3000`
- Pi-hole → `pihole.rpi.{DOMAIN}` → forward to `pihole:80`
- VPN - `vpn.rpi.{DOMAIN}` → forward to `wg-easy:51821`

For each: enable SSL → Request Let's Encrypt cert → Force SSL.

---

## Updating

Watchtower runs at 3am daily and auto-updates all containers.

To manually update everything:
```bash
docker compose pull
docker compose up -d
```

To rebuild custom containers (api, dashboard, storage-manager) after code changes:
```bash
docker compose build homelab-api homelab-dashboard homelab-storage
docker compose up -d
```

---

## Notifications

Low disk space alerts are sent via [ntfy](https://ntfy.sh).

- Install the ntfy app on your phone
- Subscribe to your topic (set in `.env` as `NTFY_TOPIC`)
- Alerts fire when free space drops below `ALERT_THRESHOLD_GB`
- One alert per event — resets when space recovers

---

## TODO

- [ ] Self-hosted ntfy
- [ ] Automated install script (`curl | bash`)
