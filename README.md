# Aegean Archive

*Ein containerisiertes Fotoarchiv, das Bilder zusammen mit ihren Metadaten in einer MariaDB-Datenbank speichert und über eine Flask-Weboberfläche anzeigt.*

## Überblick

**Aegean Archive** ist mein Abschlussprojekt für die individuelle Abschlussarbeit BLJ.

Das Projekt wurde aus einem bestehenden Fotoarchiv weiterentwickelt. Bilder werden nicht mehr nur aus einem lokalen Ordner geladen, sondern direkt in einer **MariaDB-Datenbank** gespeichert. Dadurch sind die Bilder zentral verfügbar und nicht mehr nur an einen einzelnen Ordner auf dem Computer gebunden.

Über die Weboberfläche können Bilder angezeigt, gesucht und nach Datum gefiltert werden. Zusätzlich werden wichtige Metadaten wie Dateiname, Dateigrösse, Format und Bildinformationen gespeichert und angezeigt.

Die Anwendung läuft mit **Docker Compose** und besteht aus einer **Flask-App**, einer **MariaDB-Datenbank** und einem **NGINX Reverse Proxy**.

**Aktueller Projektstatus:** In Entwicklung

## Funktionen

- Bilder über einen Metadata-Reader importieren
- Bilder direkt in MariaDB speichern
- Metadaten zu Bildern speichern und anzeigen
- Bilder in einer Galerie anzeigen
- Nach Dateinamen suchen
- Bilder nach Datum filtern
- Detailansicht für einzelne Bilder
- Vorschaubilder für bessere Ladezeiten verwenden
- Flask-App mit Docker starten
- MariaDB als zentrale Datenbank verwenden
- NGINX als Reverse Proxy einsetzen
- Daten mit einem persistenten Docker-Volume speichern

## Verwendete Technologien

- **Python**
- **Flask**
- **MariaDB**
- **Pillow**
- **HTML**
- **CSS**
- **JavaScript**
- **Docker**
- **Docker Compose**
- **NGINX**

## Aufbau

```text
Browser
   |
   v
NGINX Reverse Proxy
   |
   v
Flask-App
   |
   v
MariaDB
```

NGINX nimmt die Anfragen entgegen und leitet sie intern an die Flask-App weiter. Die Flask-App verbindet sich mit MariaDB und lädt die gespeicherten Bilder und Metadaten aus der Datenbank.

## Projektstruktur

```text
Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2/
├── nginx/
│   └── nginx.conf
├── static/
├── templates/
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── interface.py
├── Metadataextractor.py
├── requirements.txt
└── README.md
```

## Installation

### Voraussetzungen

Für das Projekt werden folgende Programme benötigt:

- **Docker Desktop**
- **Docker Compose**
- **Git**
- **Python**

### Projekt herunterladen und starten

1. Repository klonen

```bash
git clone https://github.com/AngelosDaroukakis/Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2.git
```

2. In den Projektordner wechseln

```bash
cd Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2
```

3. Container bauen und starten

```bash
docker compose up --build
```

4. Anwendung im Browser öffnen

```text
http://localhost:8080
```

5. Container stoppen

```bash
docker compose down
```

## Bilder importieren

Der Metadata-Reader wird verwendet, um Bilder auszuwählen und in die Datenbank zu speichern.

1. Virtuelle Python-Umgebung erstellen

```bash
python -m venv .venv
```

2. Virtuelle Umgebung unter Windows aktivieren

```bash
.venv\Scripts\activate
```

3. Benötigte Pakete installieren

```bash
pip install -r requirements.txt
```

4. Sicherstellen, dass Docker Compose läuft

```bash
docker compose ps
```

5. Metadata-Reader starten

```bash
python Metadataextractor.py
```

6. Einzelne Bilder oder einen ganzen Ordner auswählen

Der Metadata-Reader erstellt die benötigten Tabellen und speichert die Bilder zusammen mit den vorhandenen Metadaten in MariaDB.

## Container verwalten

Container im Hintergrund starten:

```bash
docker compose up --build -d
```

Status anzeigen:

```bash
docker compose ps
```

Logs anzeigen:

```bash
docker compose logs
```

Nur die App-Logs anzeigen:

```bash
docker compose logs app
```

Nur die NGINX-Logs anzeigen:

```bash
docker compose logs nginx
```

Container stoppen:

```bash
docker compose down
```

Container stoppen und Datenbank-Volume löschen:

```bash
docker compose down -v
```

**Achtung:** Der Parameter `-v` löscht das MariaDB-Volume. Dadurch werden alle importierten Bilder und Metadaten gelöscht.

## Datenbank öffnen

Die MariaDB kann direkt über den Datenbankcontainer geöffnet werden:

```bash
docker compose exec database mariadb -u aegean -paegean photo_archive
```

Tabellen anzeigen:

```sql
SHOW TABLES;
```

Gespeicherte Bilder prüfen:

```sql
SELECT
    id,
    filename,
    mime_type,
    LENGTH(image_data) AS bildgroesse
FROM images;
```

MariaDB verlassen:

```sql
exit;
```

## Bildspeicherung

Jedes Originalbild wird in der Datenbank gespeichert.

```text
Originalbild
   |
   v
MariaDB
   |
   v
Flask-App
   |
   v
Galerie / Detailansicht
```

Für die Galerie werden kleinere Vorschaubilder verwendet. Dadurch müssen nicht immer grosse Originalbilder direkt geladen werden, was die Oberfläche schneller und übersichtlicher macht.

## Geplante Erweiterungen

- Bilder in Alben gruppieren
- Alben wie **Ferien Athen 2025** erstellen

## Beitrag leisten

Da dieses Projekt ein Schul- und Abschlussprojekt ist, werden Änderungen kontrolliert gemacht.

Wer etwas beitragen möchte:

1. Ein neues Issue mit einer verständlichen Beschreibung erstellen

2. Repository forken

3. Einen neuen Branch erstellen

```bash
git checkout -b feature/beschreibung
```

4. Änderungen testen

5. Änderungen committen

```bash
git add .
git commit -m "Add new feature"
```

6. Branch hochladen

```bash
git push origin feature/beschreibung
```

7. Pull Request erstellen und die Änderung kurz erklären

Pull Requests sollten nur Änderungen enthalten, die zum Projekt passen und vorher getestet wurden.

## Lizenz & Credits

Für dieses Projekt ist aktuell noch keine eigene Lizenz hinterlegt.

**NAME:** Angelos Daroukakis  
**Projekt:** Individuelle Abschlussarbeit BLJ  
**Repository:** https://github.com/AngelosDaroukakis/Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2

Verwendete Technologien und externe Projekte:

- **Flask**
- **MariaDB**
- **Pillow**
- **Docker**
- **Docker Compose**
- **NGINX**
