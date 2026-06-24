# Aegean Archive

*Ein containerisiertes Fotoarchiv, das Bilder zusammen mit Metadaten in einer MariaDB-Datenbank speichert und über eine Flask-Weboberfläche anzeigt.*

## Kurzbeschreibung

*Dieses Projekt ist mein Abschlussprojekt für die individuelle Abschlussarbeit BLJ. Es erweitert ein bestehendes Fotoarchiv zu einer containerisierten Webanwendung mit zentraler Bildspeicherung in der Datenbank.*

## Überblick

**Aegean Archive** ist ein Fotoarchiv, bei dem Bilder nicht mehr nur lokal in einem Ordner liegen, sondern direkt in einer **MariaDB-Datenbank** gespeichert werden.

Das Ziel des Projekts ist, Bilder zentral zu speichern, über eine Weboberfläche anzuzeigen und wichtige Metadaten wie **Dateiname**, **Dateigrösse**, **Format** und weitere Bildinformationen sichtbar zu machen.

Die Anwendung läuft mit **Docker Compose** und besteht aus:

- **Flask-Webanwendung**
- **MariaDB-Datenbank**
- **NGINX Reverse Proxy**
- **Docker-Container**

Der aktuelle Projektstatus ist: **in Entwicklung**.

## Funktionen

- Bilder importieren
- Bilder direkt in MariaDB speichern
- Metadaten auslesen und anzeigen
- Bilder in einer Galerie darstellen
- Nach Bildern suchen
- Bilder nach Datum filtern
- Detailansicht für einzelne Bilder anzeigen
- Vorschaubilder für bessere Ladezeiten verwenden
- Anwendung mit Docker starten
- Datenbankdaten mit Docker Volume speichern
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

Der **Metadata-Reader** wird verwendet, um Bilder auszuwählen und in die Datenbank zu speichern.

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

6. Bilder oder einen ganzen Ordner auswählen

Der Metadata-Reader speichert die Bilder zusammen mit den vorhandenen Metadaten in **MariaDB**.

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

Container stoppen:

```bash
docker compose down
```

Container stoppen und Datenbank-Volume löschen:

```bash
docker compose down -v
```

**Achtung:** Der Parameter `-v` löscht das Datenbank-Volume. Dadurch werden alle gespeicherten Bilder und Metadaten gelöscht.

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

Bei diesem Projekt werden die Bilder direkt in der Datenbank gespeichert.

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

Für die Galerie werden kleinere **Vorschaubilder** verwendet. Dadurch muss die Anwendung nicht jedes Mal die grossen Originalbilder laden. Das macht die Oberfläche schneller und übersichtlicher.

## Geplante Erweiterungen

- Bilder in Alben gruppieren
- Alben wie zum Beispiel **Ferien Athen 2025** erstellen
- Oberfläche weiter verbessern
- Mehr Tests durchführen
- Mehrinstanz-Betrieb weiter ausbauen

## Beitrag leisten

Da dieses Projekt ein Abschlussprojekt ist, werden Änderungen kontrolliert gemacht.

Wer etwas beitragen möchte:

1. Ein neues Issue mit einer verständlichen Beschreibung erstellen

2. Repository forken

3. Neuen Branch erstellen

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
