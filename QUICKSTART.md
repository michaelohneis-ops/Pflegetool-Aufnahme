# 🚀 Quick-Start: Docker-Deployment

## Pflege-Tool v3.1.5 in 5 Minuten deployen

---

## Option 1: Lokaler Test (Development)

```bash
# 1. Verzeichnis erstellen
mkdir pflege-tool && cd pflege-tool

# 2. Dateien hierher kopieren:
#    - Dockerfile
#    - docker-compose.yml
#    - requirements.txt
#    - *.py (alle Python-Dateien)

# 3. Starten
docker compose up

# 4. Browser öffnen
http://localhost:8501

# FERTIG! 🎉
```

---

## Option 2: Production Server (mit SSL)

```bash
# 1. Server vorbereiten
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin certbot

# 2. Verzeichnis erstellen
sudo mkdir -p /opt/pflege-tool
cd /opt/pflege-tool

# 3. Alle Dateien hochladen (via scp/sftp)

# 4. SSL-Zertifikat holen
sudo certbot certonly --standalone -d deine-domain.de

# 5. Zertifikate kopieren
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/deine-domain.de/*.pem nginx/ssl/

# 6. Domain in nginx.conf ändern
nano nginx.conf
# → Ersetze "pflege-tool.de" mit "deine-domain.de"

# 7. Starten
docker compose up -d

# 8. Testen
https://deine-domain.de

# FERTIG! 🎉
```

---

## Option 3: Super-Quick (ohne SSL)

```bash
# 1. docker-compose.yml vereinfachen
# → Lösche nginx-Service komplett
# → Ändere Port zu 80:8501

# 2. Starten
docker compose up -d

# 3. Firewall öffnen
sudo ufw allow 80

# 4. Browser
http://server-ip

# FERTIG! 🎉
```

---

## Wichtige Befehle

```bash
# Starten
docker compose up -d

# Stoppen
docker compose down

# Logs ansehen
docker compose logs -f

# Neu bauen
docker compose build

# Status prüfen
docker compose ps

# Container betreten
docker compose exec pflege-tool sh
```

---

## Troubleshooting

**Problem:** Port 8501 bereits belegt
```bash
sudo lsof -i :8501
# → Anderen Prozess stoppen oder Port in docker-compose.yml ändern
```

**Problem:** Permission denied
```bash
sudo chown -R $USER:$USER .
```

**Problem:** Container startet nicht
```bash
docker compose logs pflege-tool
# → Fehlermeldung lesen und beheben
```

---

## Dateien-Checkliste

Benötigte Dateien im Verzeichnis:

```
☐ Dockerfile
☐ docker-compose.yml
☐ requirements.txt (oder requirements_v3_1_5.txt)
☐ pflege_aufnahme_tool_v3_1.py
☐ pflegesoftware_export_v3_1_5.py
☐ database_module_v3_1_5.py
☐ nginx.conf (nur für Production mit SSL)
☐ .dockerignore (optional)
```

---

## Nach dem Start

**Erste Schritte:**

1. **Browser öffnen:** http://localhost:8501 (oder https://deine-domain.de)
2. **Test-Assessment:** Neuen Patient anlegen
3. **Export testen:** DM7/Vivendi CSV/Excel downloaden
4. **Backup prüfen:** Läuft automatisch täglich um 2:00 Uhr

**Daten-Speicherort:**
```
./data/pflege_tool.db          # Datenbank
./backups/                     # Automatische Backups
./exports/                     # DM7/Vivendi/Medifox Exports
./logs/                        # Application Logs
```

---

**Viel Erfolg! 🚀**

Bei Fragen: Siehe DOCKER_DEPLOYMENT_GUIDE.md
