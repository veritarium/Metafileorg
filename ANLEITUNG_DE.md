# Virtual File Organizer - Deutsche Anleitung

## 📥 Installation und Nutzung

### Voraussetzungen

- **Python 3.11 oder höher** ([Download](https://www.python.org/downloads/))
- **Git** (optional, für direktes Klonen)
- **Windows:** Administrator-Rechte für symbolische Links (oder Entwicklermodus aktiviert)

---

## 🎯 Schnellstart (3 Schritte)

### Schritt 1: Projekt herunterladen

#### Option A: Mit Git (empfohlen)

```bash
# Repository klonen
git clone https://github.com/veritarium/Metafileorg.git

# In das Projektverzeichnis wechseln
cd Metafileorg
```

#### Option B: ZIP-Download

1. Gehe zu https://github.com/veritarium/Metafileorg
2. Klicke auf den grünen Button **"Code"**
3. Wähle **"Download ZIP"**
4. Entpacke die ZIP-Datei
5. Öffne Terminal/Eingabeaufforderung im entpackten Ordner

### Schritt 2: Abhängigkeiten installieren

```bash
# In das file_organizer Verzeichnis wechseln
cd file_organizer

# Python-Pakete installieren
pip install -r requirements.txt
```

**Bei Problemen:**
```bash
# Explizit pip für Python 3.11+ verwenden
python3 -m pip install -r requirements.txt
# oder auf Windows:
py -3 -m pip install -r requirements.txt
```

### Schritt 3: Erste Nutzung

```bash
# Hilfe anzeigen
python src/main.py --help

# Beispiel: Einen Ordner scannen
python src/main.py scan /pfad/zu/deinen/dateien --db meine_dateien.db
```

---

## 📖 Komplettes Beispiel

Hier ist ein vollständiges Beispiel, wie du deine Dateien organisierst:

### 1. Dateien scannen

```bash
# Scanne einen Ordner (z.B. dein Dokumenten-Ordner)
python src/main.py scan C:\Users\DeinName\Documents --db catalog.db --hash

# Linux/Mac:
python src/main.py scan /home/username/Documents --db catalog.db --hash
```

**Optionen:**
- `--hash` : Berechnet SHA-256 Hashes (für Duplikat-Erkennung, dauert länger)
- `--ignore` : Dateitypen ausschließen, z.B. `--ignore tmp log`

### 2. Kategorisieren (automatisch)

```bash
# Dateien kategorisieren
python src/main.py categorize --db catalog.db
```

Das kategorisiert alle Dateien anhand ihrer Endungen (z.B. .pdf → Dokumente, .jpg → Bilder).

### 3. Vorschau erstellen (Dry-Run)

```bash
# HTML-Report erstellen
python src/main.py dryrun --db catalog.db --output vorschau.html
```

Öffne `vorschau.html` im Browser, um zu sehen, wie deine Dateien organisiert werden.

### 4. Virtuelle Ansicht erstellen

```bash
# Mappings für eine Ansicht generieren
python src/main.py generate ByCategory --db catalog.db --output mappings.json

# Zuerst testen (Dry-Run)
python src/main.py link ByCategory --mappings mappings.json --dry-run

# Wenn alles gut aussieht, Links erstellen
python src/main.py link ByCategory --mappings mappings.json
```

**Ergebnis:** Deine Dateien sind jetzt in `./_Views/ByCategory/` organisiert:
```
_Views/
└── ByCategory/
    ├── Documents/
    │   ├── PDF/
    │   │   ├── rechnung.pdf → C:\Users\...\rechnung.pdf
    │   │   └── vertrag.pdf → C:\Users\...\vertrag.pdf
    │   └── Word/
    │       └── brief.docx → C:\Users\...\brief.docx
    ├── Images/
    │   └── Photos/
    │       └── urlaub.jpg → C:\Users\...\urlaub.jpg
    └── CAD/
        └── AutoCAD/
            └── plan.dwg → C:\Users\...\plan.dwg
```

### 5. Web-Interface starten (optional)

```bash
# Web-Oberfläche starten
python src/main.py web --port 5000

# Im Browser öffnen: http://localhost:5000
```

Die Web-Oberfläche bietet:
- 🔍 Dateisuche
- 📊 Filterung nach Kategorie, Größe, Datum
- 🔄 Duplikat-Anzeige
- 📁 Neue Scans starten

---

## 🎨 Verfügbare Ansichten

### 1. Nach Kategorie (ByCategory)

Organisiert nach Dateityp:
```
_Views/ByCategory/
├── Documents/       # Alle Dokumente
├── Images/          # Alle Bilder
├── CAD/             # CAD-Dateien
├── Code/            # Quellcode
├── Media/           # Videos, Audio
└── Archives/        # ZIP, RAR, etc.
```

**Erstellen:**
```bash
python src/main.py generate ByCategory --db catalog.db --output mappings.json
python src/main.py link ByCategory --mappings mappings.json
```

### 2. Nach Datum (ByDate)

Organisiert nach Erstellungsdatum:
```
_Views/ByDate/
├── 2025/
│   ├── January/
│   ├── February/
│   └── March/
└── 2024/
    └── December/
```

**Erstellen:**
```bash
python src/main.py generate ByDate --db catalog.db --output mappings.json
python src/main.py link ByDate --mappings mappings.json
```

### 3. Nach Größe (BySize)

Organisiert nach Dateigröße:
```
_Views/BySize/
├── Tiny (<100KB)/
├── Small (100KB-1MB)/
├── Medium (1-10MB)/
├── Large (10-100MB)/
└── Huge (>100MB)/
```

### 4. Nach Projekt (ByProject)

Erkennt automatisch Projekte (heuristisch):
```
_Views/ByProject/
├── ProjectAlpha/
├── Kundenprojekt_2025/
└── Unknown/
```

### 5. Eigene Ansicht (Custom)

In `config/views.yaml` kannst du eigene Regeln definieren:

```yaml
views:
  MeineAnsicht:
    description: "Große PDFs aus 2025"
    rules:
      - condition:
          extension: "pdf"
          size: "> 5242880"  # > 5 MB
        target: "GrossePDFs/{year}/{name}"
```

**Verwenden:**
```bash
python src/main.py generate MeineAnsicht --db catalog.db --output mappings.json
python src/main.py link MeineAnsicht --mappings mappings.json
```

---

## 🔧 Konfiguration

### Dateitypen anpassen (config/categories.yaml)

Füge eigene Dateityp-Zuordnungen hinzu:

```yaml
mapping:
  xyz:  # Deine Dateiendung
    category: MeineKategorie
    subcategory: MeineUnterkategorie
```

### Eigene Ansichten erstellen (config/views.yaml)

Beispiel - nur Bilder größer als 1 MB:

```yaml
views:
  GrosseBilder:
    description: "Bilder größer als 1 MB"
    rules:
      - condition:
          category: "Images"
          size: ">= 1048576"
        target: "GrosseBilder/{year}/{name}"
```

---

## 🛠️ Häufige Befehle

### Duplikate finden

```bash
python src/main.py duplicates --db catalog.db
```

### Nur scannen, ohne Kategorisierung

```bash
python src/main.py scan /pfad --db catalog.db --no-categorize
```

### Bestimmte Dateitypen ignorieren

```bash
python src/main.py scan /pfad --db catalog.db --ignore tmp log bak
```

### Links für eine Ansicht entfernen (Rollback)

```bash
# Noch nicht direkt implementiert, manuell:
# Einfach den Ordner _Views/ViewName/ löschen
rm -rf _Views/ByCategory/
```

---

## 💡 Tipps & Tricks

### 1. Teste zuerst mit wenigen Dateien

```bash
# Scanne nur einen kleinen Testordner
python src/main.py scan C:\TestOrdner --db test.db
python src/main.py dryrun --db test.db --output test_report.html
```

### 2. Verwende verschiedene Datenbanken

```bash
# Für verschiedene Projekte separate Datenbanken
python src/main.py scan /projekt1 --db projekt1.db
python src/main.py scan /projekt2 --db projekt2.db
```

### 3. Backup der Datenbank

```bash
# Regelmäßig sichern
cp catalog.db catalog.db.backup
```

### 4. Große Ordner scannen

```bash
# Bei vielen Dateien (60.000+) dauert der Scan länger
# Hash-Berechnung optional weglassen für schnelleren Scan
python src/main.py scan /grosser/ordner --db catalog.db
# Ohne --hash ist es viel schneller
```

---

## 🐛 Fehlerbehebung

### "Permission denied" beim Link erstellen (Windows)

**Problem:** Keine Administrator-Rechte

**Lösung 1:** Als Administrator ausführen
- Rechtsklick auf PowerShell/CMD → "Als Administrator ausführen"

**Lösung 2:** Entwicklermodus aktivieren
1. Windows Einstellungen öffnen
2. Update & Sicherheit → Für Entwickler
3. "Entwicklermodus" einschalten

### "Module not found"

**Problem:** Abhängigkeiten nicht installiert

**Lösung:**
```bash
cd file_organizer
pip install -r requirements.txt
```

### "Database is locked"

**Problem:** Datenbank wird bereits verwendet

**Lösung:**
- Schließe andere Instanzen des Programms
- Beende das Web-Interface falls aktiv
- Lösche `catalog.db-journal` falls vorhanden

### Links zeigen auf falsche Dateien

**Problem:** Dateien wurden nach dem Scan verschoben

**Lösung:**
- Neuen Scan durchführen
- Alte Links löschen und neu erstellen

---

## 📊 Beispiel-Workflow

### Szenario: 10.000 Fotos organisieren

```bash
# 1. In das Projektverzeichnis
cd Metafileorg/file_organizer

# 2. Fotos scannen mit Hash-Berechnung
python src/main.py scan D:\Fotos --db fotos.db --hash

# 3. Duplikate finden
python src/main.py duplicates --db fotos.db

# 4. Vorschau erstellen
python src/main.py dryrun --db fotos.db --output fotos_preview.html

# 5. Nach Datum organisieren
python src/main.py generate ByDate --db fotos.db --output mappings_date.json
python src/main.py link ByDate --mappings mappings_date.json

# 6. Zusätzlich nach Größe organisieren
python src/main.py generate BySize --db fotos.db --output mappings_size.json
python src/main.py link BySize --mappings mappings_size.json

# Jetzt hast du zwei Ansichten:
# _Views/ByDate/     -> Nach Jahr/Monat
# _Views/BySize/     -> Nach Dateigröße
```

---

## 🔒 Sicherheit

### Original-Dateien bleiben unverändert

- Das Tool erstellt **nur symbolische Links**
- Original-Dateien werden **nicht verschoben oder kopiert**
- Löschen eines Links löscht **nicht** die Original-Datei

### Web-Interface

**⚠️ WICHTIG:** Das Web-Interface hat standardmäßig **keine Authentifizierung**

- Läuft nur auf `localhost` (127.0.0.1)
- **Nicht ins Netzwerk freigeben** ohne zusätzliche Sicherheit
- Für lokale Nutzung sicher

### Datensicherung

```bash
# Vor großen Operationen immer Backup erstellen
# 1. Wichtige Dateien sichern
# 2. Datenbank sichern
cp catalog.db catalog.db.backup
```

---

## 📚 Weitere Ressourcen

### Dokumentation

- **README.md** - Hauptdokumentation (Englisch)
- **IMPLEMENTATION_SUMMARY.md** - Changelog und technische Details
- **master_claude_review.md** - Vollständige Code-Review
- **CONTRIBUTING.md** - Wie man beiträgt

### Hilfe bekommen

1. **Issues auf GitHub:** https://github.com/veritarium/Metafileorg/issues
2. **Discussions:** (falls aktiviert)
3. **README lesen:** Viele Antworten sind dort

### Hilfe anbieten

- Bugs melden via GitHub Issues
- Features vorschlagen
- Code beitragen (Pull Requests)
- Dokumentation verbessern

---

## ⚡ Erweiterte Nutzung

### Mehrere Ansichten gleichzeitig

```bash
# Erstelle mehrere Ansichten parallel
python src/main.py generate ByCategory --db catalog.db --output map_cat.json
python src/main.py generate ByDate --db catalog.db --output map_date.json
python src/main.py generate BySize --db catalog.db --output map_size.json

python src/main.py link ByCategory --mappings map_cat.json
python src/main.py link ByDate --mappings map_date.json
python src/main.py link BySize --mappings map_size.json

# Ergebnis:
# _Views/ByCategory/  -> Nach Typ organisiert
# _Views/ByDate/      -> Nach Datum organisiert
# _Views/BySize/      -> Nach Größe organisiert
```

### Automatisierung mit Skript

Erstelle eine Batch-Datei (Windows) oder Shell-Skript (Linux/Mac):

**organize.bat (Windows):**
```batch
@echo off
cd file_organizer
python src/main.py scan %1 --db catalog.db --hash
python src/main.py categorize --db catalog.db
python src/main.py generate ByCategory --db catalog.db --output mappings.json
python src/main.py link ByCategory --mappings mappings.json --dry-run
echo Prüfe die Vorschau. Zum Erstellen der Links nochmal ohne --dry-run ausführen.
pause
```

**Nutzung:**
```batch
organize.bat C:\MeineDateien
```

---

## 🎓 Lern-Ressourcen

### Python lernen
- [Python.org Tutorial](https://docs.python.org/3/tutorial/) (Deutsch verfügbar)
- [Python für Einsteiger](https://www.python-lernen.de/)

### Git lernen
- [Git Dokumentation](https://git-scm.com/book/de/v2)
- [GitHub Guides](https://guides.github.com/)

### Symbolische Links verstehen
- Windows: `mklink /?` in CMD
- Linux/Mac: `man ln`

---

## 📞 Support

### Probleme melden

1. Gehe zu https://github.com/veritarium/Metafileorg/issues
2. Klicke "New Issue"
3. Wähle "Bug Report"
4. Fülle das Template aus
5. Sende ab

### Feature-Wünsche

1. Gehe zu https://github.com/veritarium/Metafileorg/issues
2. Klicke "New Issue"
3. Wähle "Feature Request"
4. Beschreibe deine Idee

---

## ✅ Checkliste für erste Nutzung

- [ ] Python 3.11+ installiert
- [ ] Repository geklont/heruntergeladen
- [ ] Abhängigkeiten installiert (`pip install -r requirements.txt`)
- [ ] Testordner mit wenigen Dateien erstellt
- [ ] Ersten Scan durchgeführt
- [ ] Dry-Run Report angeschaut
- [ ] Erste Ansicht erstellt
- [ ] Links im `_Views/` Ordner überprüft
- [ ] Bei Problemen GitHub Issues gelesen

---

## 🎉 Viel Erfolg!

Das Tool ist bereit für die Nutzung. Starte mit einem kleinen Test und erweitere dann auf deine gesamte Dateisammlung.

**Fragen?** → https://github.com/veritarium/Metafileorg/issues

**Gefällt dir das Projekt?** → Gib ihm einen ⭐ auf GitHub!

---

*Zuletzt aktualisiert: 2026-01-22*
