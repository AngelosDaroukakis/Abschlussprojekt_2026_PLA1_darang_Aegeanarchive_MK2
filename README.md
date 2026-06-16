# Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2
*Ein containerisiertes Fotoarchiv, das Bilder zusammen mit ihren Metadaten direkt in einer MariaDB-Datenbank speichert und über eine Flask-Weboberfläche anzeigt.*

## Überblick

**Aegean Archive** ist mein Abschlussprojekt im ersten Lehrjahr als Informatiker Plattformentwicklung.

Das Projekt wurde aus einem bestehenden lokalen Fotoarchiv weiterentwickelt. Bilder werden nicht mehr nur über einen lokalen Ordner geladen, sondern direkt als Binärdaten in MariaDB gespeichert.

Über die Weboberfläche können die gespeicherten Bilder in einer Galerie angezeigt, gesucht und nach Datum gefiltert werden. Auf der Detailseite werden zusätzliche Bild- und Kameradaten angezeigt.

Die Anwendung läuft mit Docker Compose und besteht aus einer Flask-App, einer MariaDB-Datenbank und einem NGINX Reverse Proxy.

**Aktueller Projektstatus:** In Entwicklung

## Funktionen

- Bilder über den Metadata-Reader importieren
- Bilder direkt als `LONGBLOB` in MariaDB speichern
- Dateiname, Grösse, Format und Bildabmessungen speichern
- EXIF- und GPS-Daten auslesen
- Bilder in einer Galerie anzeigen
- Nach Dateinamen suchen
- Bilder nach Aufnahmedatum filtern
- Detailansicht mit Bild- und Kameradaten
- Kleine Vorschaubilder für die Galerie erzeugen
- Grössere Vorschaubilder auf der Detailseite anzeigen
- EXIF-Ausrichtung automatisch beachten
- Flask-App und MariaDB mit Docker Compose starten
- Daten mit einem persistenten Docker-Volume speichern
- NGINX als Reverse Proxy verwenden

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
````

NGINX nimmt die Anfragen auf Port `8080` entgegen und leitet sie intern an die Flask-App auf Port `5000` weiter.

Die Flask-App und MariaDB kommunizieren über das interne Docker-Netzwerk `aegean-network`.

## Projektstruktur

```text
Aegean-Archive/
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

Für den Betrieb werden folgende Programme benötigt:

* Docker Desktop
* Docker Compose
* Git
* Python für den lokalen Metadata-Reader

### Projekt herunterladen

1. Repository klonen:

```bash
git clone https://github.com/AngelosDaroukakis/Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2.git
```

2. In den Projektordner wechseln:

```bash
cd Abschlussprojekt_2026_PLA1_darang_Aegeanarchive_MK2
```

3. Container bauen und starten:

```bash
docker compose up --build
```

4. Die Anwendung im Browser öffnen:

```text
http://localhost:8080
```

## Bilder importieren

Der Metadata-Reader läuft aktuell direkt auf dem Computer und verbindet sich über Port `3307` mit der MariaDB im Container.

1. Virtuelle Python-Umgebung erstellen:

```bash
python -m venv .venv
```

2. Virtuelle Umgebung unter Windows aktivieren:

```bash
.venv\Scripts\activate
```

3. Benötigte Python-Pakete installieren:

```bash
pip install -r requirements.txt
```

4. Sicherstellen, dass Docker Compose läuft:

```bash
docker compose ps
```

5. Metadata-Reader starten:

```bash
python Metadataextractor.py
```

6. Einzelne Bilder oder einen ganzen Ordner auswählen.

Der Metadata-Reader erstellt die benötigten Tabellen und speichert die Bilder zusammen mit den vorhandenen Metadaten in MariaDB.

## Datenbankverbindungen

### Flask-App im Docker-Netzwerk

```text
Host: database
Port: 3306
Datenbank: photo_archive
Benutzer: aegean
```

### Metadata-Reader vom Computer

```text
Host: localhost
Port: 3307
Datenbank: photo_archive
Benutzer: aegean
```

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

Container stoppen und die Datenbank vollständig löschen:

```bash
docker compose down -v
```

**Achtung:** Der Parameter `-v` löscht das MariaDB-Volume. Dadurch gehen alle importierten Bilder und Metadaten verloren.

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

Jedes Originalbild wird nur einmal in der Spalte `image_data` gespeichert.

```sql
image_data LONGBLOB
```

Für die Galerie und die Detailseite werden kleinere Versionen dynamisch mit Pillow erstellt.

```text
Originalbild in MariaDB
        |
        v
Flask und Pillow
        |
        ├── kleines Vorschaubild für die Galerie
        └── grösseres Vorschaubild für die Detailseite
```

Dadurch müssen in der Galerie nicht mehrere grosse Originalbilder gleichzeitig geladen werden.

## Geplante Erweiterungen

* Beschreibungen zu Bildern hinzufügen
* Bilder in Alben gruppieren
* Alben wie `Ferien Athen 2025` erstellen
* Mehrere Flask-Instanzen verwenden
* NGINX als Load Balancer einsetzen
* Weitere Tests und Verbesserungen durchführen

## Beitrag leisten

Beiträge und Verbesserungsvorschläge können über GitHub eingebracht werden.

1. Ein neues Issue mit einer verständlichen Beschreibung erstellen.
2. Das Repository forken.
3. Einen eigenen Branch erstellen:

```bash
git checkout -b feature/beschreibung
```

4. Änderungen testen und committen:

```bash
git add .
git commit -m "Add new feature"
```

5. Den Branch pushen:

```bash
git push origin feature/beschreibung
```

6. Einen Pull Request erstellen und die Änderungen kurz erklären.

Pull Requests sollten nur Änderungen enthalten, die zum Projekt passen und vorher getestet wurden.

## Lizenz & Credits

Für dieses Projekt ist aktuell noch keine eigene Lizenz hinterlegt.

**Autor:** angelosdaroukakis

Verwendete Technologien und externe Projekte:

* Flask
* MariaDB
* Pillow
* Docker
* Docker Compose
* NGINX
