# 🏥 Pflegerisches Aufnahme-Tool v3.2

## Mit Peplau-Beziehungsmodell & Spezialisierungs-Modulen

**Version:** 3.2.0  
**Release-Datum:** 01.02.2026  
**Status:** 🚀 Produktionsreif

---

## 🎯 Was ist neu in v3.2?

### Peplau-Beziehungsmodell ✨ HIGHLIGHT
Basierend auf Hildegard Peplau's Theorie der interpersonalen Beziehungen:
- **4 Phasen** der therapeutischen Beziehung
- **6 Pflegerollen** (Fremde/r, Lehrer/in, Berater/in, etc.)
- **Beziehungsqualität** messbar (0-100%)
- **Bedürfnisse** nach Peplau identifiziert

### Spezialisierungs-Module 🧒🧠👴

**1. Pädiatrie-Modul**
- Entwicklungspsychologie (Havighurst)
- Bindungstheorie (Bowlby)
- Familienkontext-Analyse
- Peer-Beziehungen
- Altersentsprechende Interventionen

**2. Psychiatrie-Modul**
- Psychopathologischer Befund
- Suizidrisiko-Assessment (⚠️ KRITISCH)
- Beziehungsgestaltung
- Soziales Funktionsniveau
- Treatment-Motivation

**3. Geriatrie-Modul**
- Demenz-spezifische Aspekte
- Validation
- Angehörigen-Arbeit

### Automatische Erkennung 🔍
- Erkennt aus Text + Alter → Spezialisierung
- Aktiviert passendes Modul automatisch
- Beispiel: "10 Jahre" → Pädiatrie-Modul

---

## 📦 Installation

### Voraussetzungen
```bash
Python >= 3.9
pip >= 21.0
```

### Schritt 1: Dependencies installieren
```bash
pip install streamlit==1.31.0
pip install pandas==2.2.0  
pip install fpdf==1.7.2
```

### Schritt 2: Tool starten
```bash
streamlit run pflege_aufnahme_tool_v3_2.py
```

### Schritt 3: Browser öffnet automatisch
```
URL: http://localhost:8501
```

---

## 🚀 Schnellstart

### 1. Neue Aufnahme durchführen

**Schritt 1:** Patient-Daten eingeben
```
Patient-ID:   PAT-2026-001
Name:         Anna K.
Alter:        10 Jahre  ← WICHTIG für Spezialisierung!
```

**Schritt 2:** Aufnahme-Text eingeben
```
Anna, 10 Jahre, Asthma bronchiale.
Trotzig bei Medikamenten-Einnahme.
Spielt Hockey in Mannschaft.
Mutter sehr engagiert.
```

**Schritt 3:** Assessment durchführen
```
[Button: Aufnahme-Assessment durchführen]
```

**Ergebnis:**
```
✅ Spezialisierung erkannt: PÄDIATRIE
✅ Beziehungs-Assessment: 58%  
✅ Phase: Orientierung
✅ Empfehlungen: Peer-Einbindung, Autonomie respektieren
```

### 2. Beziehungs-Assessment ansehen

**Tab "🤝 Beziehung (Peplau)"**
```
Vertrauenslevel:       ████░░░░░░ 4/10
Kommunikation:         █████░░░░░ 5/10
Partizipation:         ███░░░░░░░ 3/10
Familie-Involvement:   ████████░░ 8/10

Phase: ORIENTIERUNG
Hauptbedürfnis: Autonomie
Empfehlung: Altersentsprechend ansprechen
```

### 3. Export & Archivierung

**Smart-Copy:**
```
[Button: Text für DM7 kopieren]
→ Strukturierter Text inkl. Peplau-Assessment
```

**PDF-Export:**
```
[Button: Assessment als PDF]
→ Vollständiges PDF mit Beziehungs-Sektion
```

---

## 📚 Feature-Übersicht

### Kern-Features (aus v3.1)
- ✅ RIA-Trigger-Erkennung
- ✅ BI-Module (NBA)
- ✅ SiS-Struktur
- ✅ FEM-Wächter
- ✅ DVA-Compliance
- ✅ Smart-Copy Export
- ✅ MDK-Simulator
- ✅ PDF-Export

### NEU in v3.2
- ✨ **Peplau-Beziehungsmodell**
- ✨ **Spezialisierungs-Detector**
- ✨ **Pädiatrie-Modul**
- ✨ **Psychiatrie-Modul**
- ✨ **Geriatrie-Modul**
- ✨ **Familienkontext-Analyse**
- ✨ **Entwicklungspsychologie**

---

## 🎓 Theoretische Grundlagen

### Hildegard Peplau (1909-1999)

**Kernaussage:**
> "Pflege ist ein bedeutsamer, therapeutischer, zwischenmenschlicher Prozess."

**4 Phasen:**
1. **Orientierung:** Kennenlernen, Vertrauen aufbauen
2. **Identifikation:** Bedürfnisse werden klar
3. **Nutzung:** Aktive Problemlösung
4. **Ablösung:** Unabhängigkeit erreicht

**6 Pflegerollen:**
1. Fremde/r (Stranger)
2. Ressourcenperson (Resource Person)
3. Lehrer/in (Teacher)
4. Führungsperson (Leader)
5. Ersatzperson (Surrogate)
6. Berater/in (Counsellor)

### Robert Havighurst (1900-1991)

**Entwicklungsaufgaben:**
- Jede Lebensphase hat spezifische Aufgaben
- Bei Kindern: Autonomie, Peer-Beziehungen, Schulkompetenzen

### John Bowlby (1907-1990)

**Bindungstheorie:**
- Sicher, Unsicher-vermeidend, Unsicher-ambivalent, Desorganisiert
- Wichtig für Pädiatrie und Psychiatrie

---

## 🧪 Test-Fälle

### Test 1: Pädiatrie (Anna)

**Input:**
```
Patient: Anna, 10 Jahre
Text: "Asthma, trotzig bei Medikamenten, spielt Hockey"
```

**Erwartetes Ergebnis:**
```
Spezialisierung: PÄDIATRIE
Altersgruppe: Schulkind (6-12 Jahre)
Peplau-Phase: Orientierung
Vertrauen: 4/10 (trotzig)
Hauptbedürfnis: Autonomie
Bindung: Sicher (Mutter präsent)
Empfehlung: Peer-Einbindung, spielerische Ansätze
```

### Test 2: Psychiatrie (Depression)

**Input:**
```
Patient: Herr M., 35 Jahre
Text: "Depression, Suizidgedanken, distanziert, lebt allein"
```

**Erwartetes Ergebnis:**
```
Spezialisierung: PSYCHIATRIE
Peplau-Phase: Orientierung
Vertrauen: 2/10 (distanziert)
Suizidrisiko: MITTEL-HOCH ⚠️
Beziehungsproblem: Starke Distanzierung
Empfehlung: Enge Begleitung, Sicherheit herstellen
```

### Test 3: Geriatrie (Demenz)

**Input:**
```
Patient: Frau Schmidt, 82 Jahre
Text: "Demenz, verwirrt, desorientiert, Tochter besucht täglich"
```

**Erwartetes Ergebnis:**
```
Spezialisierung: GERIATRIE
Peplau-Phase: Variabel (Demenz)
Vertrauen: 5/10
Familie-Involvement: 8/10 (Tochter)
Empfehlung: Validation, Angehörigen-Schulung
```

---

## 📊 UI-Struktur v3.2

### Tab 1: Neue Aufnahme
```
- Patient-Daten (ID, Name, Alter)
- Spezialisierungs-Anzeige (automatisch)
- Aufnahme-Text
- Assessment durchführen
- Ergebnisse (RIA, BI, DVA, FEM)
- Export (Smart-Copy, PDF)
```

### Tab 2: 🤝 Beziehung (Peplau) ⭐ NEU
```
- Aktuelle Phase
- Beziehungsqualität-Scores
- Pflegerollen
- Identifizierte Bedürfnisse
- Beziehungsprobleme
- Empfohlene Interventionen
```

### Tab 3: 📋 Spezialisierung ⭐ NEU
```
Pädiatrie:
- Entwicklungsstand
- Bindungsqualität
- Familienkontext
- Peer-Beziehungen
- Coping-Strategien

Psychiatrie:
- Psychopathologischer Befund
- Suizidrisiko
- Beziehungsgestaltung
- Soziales Funktionsniveau
- Ressourcen

Geriatrie:
- Demenz-Aspekte
- Validation
- Angehörigen-Einbindung
```

### Tab 4: MDK-Dashboard
```
- Gesamtstatistik
- Compliance-Scores
- FEM-Tracking
- MDK-Report (Text/PDF)
```

### Tab 5: Verlauf
```
- Alle Assessments chronologisch
- Filter nach Spezialisierung
```

---

## 🔧 Konfiguration

### Spezialisierungs-Schwellwerte anpassen

```python
# In pflege_aufnahme_tool_v3_2.py:

class SpecializationDetector:
    PEDIATRIC_AGE_THRESHOLD = 18  # Jahre
    GERIATRIC_AGE_THRESHOLD = 65  # Jahre
```

### Beziehungs-Indikatoren erweitern

```python
class PeplauRelationshipEngine:
    TRUST_INDICATORS = {
        'positive': ['vertrauensvoll', 'öffnet sich', ...],
        'negative': ['misstrauisch', 'verschlossen', ...]
    }
    # Eigene Keywords hinzufügen
```

---

## 📖 Dokumentation

### Vollständige Dokumentation verfügbar:

1. **README_v3_2.md** (diese Datei)
   - Installation, Schnellstart

2. **KONZEPT_PEPLAU_v3_2.md**
   - Theoretische Grundlagen
   - Algorithmen im Detail

3. **API_DOKUMENTATION_v3_2.md**
   - Klassen-Referenz
   - Methoden-Beschreibungen

4. **ANWENDUNGSHANDBUCH_v3_2.md**
   - Schritt-für-Schritt-Anleitungen
   - Best Practices

5. **CHANGELOG_v3_2.md**
   - Alle Änderungen von v3.1 → v3.2

---

## 🎯 Use Cases

### Use Case 1: Kinder-Aufnahme

**Situation:**
10-jähriges Kind mit Asthma, Non-Compliance

**Workflow:**
1. Alter eingeben → Pädiatrie-Modul aktiviert
2. Assessment → Beziehung analysiert (Trotz)
3. Empfehlungen → Peer-Einbindung, spielerisch
4. Export → PDF mit Peplau-Sektion für Team

**Ergebnis:**
Altersentsprechende Interventionen statt Standard-Erwachsenen-Pflege

### Use Case 2: Psychiatrische Krise

**Situation:**
Patient mit Depression und Suizidgedanken

**Workflow:**
1. Keywords erkannt → Psychiatrie-Modul aktiviert
2. Suizidrisiko-Assessment → HOCH (roter Alert!)
3. Beziehungsanalyse → Distanziert (2/10)
4. Empfehlungen → 1:1-Betreuung, Sicherheit

**Ergebnis:**
Kritische Situation sofort erkannt, Maßnahmen eingeleitet

### Use Case 3: Demenz-Patient

**Situation:**
82-jährige mit Demenz, Angehörige stark involviert

**Workflow:**
1. Alter + Keywords → Geriatrie-Modul
2. Familie-Assessment → Hohe Unterstützung (8/10)
3. Beziehung → Validation-Ansatz
4. Empfehlungen → Angehörigen-Schulung

**Ergebnis:**
Familienressourcen optimal genutzt

---

## 💡 Best Practices

### 1. Alter immer angeben
```
✅ RICHTIG: "10 Jahre" eingeben
❌ FALSCH: Alter weglassen

→ Ermöglicht automatische Spezialisierung
```

### 2. Beziehungsaspekte im Text erwähnen
```
✅ RICHTIG: "Patient wirkt misstrauisch, distanziert"
❌ FALSCH: Nur medizinische Fakten

→ Verbessert Beziehungs-Assessment
```

### 3. Familie/Soziales dokumentieren
```
✅ RICHTIG: "Mutter besucht täglich, sehr engagiert"
❌ FALSCH: Soziales Umfeld ignorieren

→ Wichtig für Peplau-Analyse
```

### 4. Regelmäßig exportieren
```
✅ RICHTIG: Nach jedem Assessment PDF erstellen
→ Archivierung, MDK-Bereitschaft
```

---

## ⚠️ Wichtige Hinweise

### Datenschutz (DSGVO)

**WICHTIG:**
- PDFs enthalten personenbezogene Daten
- Nur verschlüsselt versenden
- Zugriff nur für autorisiertes Personal
- Nach Aufbewahrungsfrist löschen

### Medizinrecht

**HINWEIS:**
Dieses Tool ist eine **Entscheidungsunterstützung**, KEIN medizinisches Gerät.

Finale Verantwortung liegt bei:
- Pflegefachkraft
- Heimleitung/PDL
- Ärztlichem Personal

### Suizidrisiko (Psychiatrie)

**KRITISCH:**
Bei Suizidrisiko HOCH:
- ⚠️ SOFORT Arzt informieren
- 1:1-Betreuung erwägen
- Notfallplan aktivieren
- Tool ersetzt NICHT klinische Beurteilung!

---

## 🐛 Troubleshooting

### Problem: Spezialisierung nicht erkannt

**Lösung:**
```
1. Alter im Patient-Daten-Feld angeben
2. Keywords im Text verwenden:
   - Pädiatrie: "Kind", "Schule", "Eltern"
   - Psychiatrie: "Depression", "Angst"
   - Geriatrie: "Demenz", "Sturzgefahr"
```

### Problem: Beziehungs-Score zu niedrig/hoch

**Lösung:**
```
Scores basieren auf Keywords im Text:
- Mehr beschreibende Adjektive verwenden
- Beziehungsaspekte explizit erwähnen
- "vertrauensvoll", "kooperativ" vs. "distanziert"
```

### Problem: PDF-Generierung schlägt fehl

**Lösung:**
```bash
# FPDF installiert?
pip install fpdf==1.7.2

# Zu viele Daten (>100 Assessments)?
→ In kleinere Gruppen aufteilen

# Alternative: Text-Export nutzen
```

---

## 📞 Support

### Bei Fragen oder Problemen:

**Technischer Support:**
- GitHub Issues: [Link]
- Email: support@pflege-tool.de

**Schulungen:**
- Peplau-Grundlagen (2h)
- Tool-Nutzung (1h)  
- Spezialisierungs-Module (1h)

**Dokumentation:**
- Alle Dokumente in `/docs` Ordner
- Video-Tutorials: [Link]

---

## 🏆 Credits

**Entwickelt von:** Pflege-Tool Team  
**Theoretische Beratung:** 
- Prof. Dr. X (Pflegewissenschaft)
- Dr. Y (Kinder- und Jugendpsychiatrie)

**Basierend auf:**
- Hildegard Peplau (1952): "Interpersonal Relations in Nursing"
- Robert Havighurst (1972): "Developmental Tasks"
- John Bowlby (1969): "Attachment Theory"

---

## 📄 Lizenz

**Version:** 3.2.0  
**Copyright:** © 2026 Pflege-Tool Team  
**Lizenz:** Proprietär (Für kommerzielle Nutzung siehe Pricing)

---

## 🚀 Roadmap

### v3.3 (Q2 2026)
- KI-gestützte Beziehungsanalyse (GPT-4)
- Sprach-Eingabe (Audio → Text)
- Multi-Language Support (English, Türkçe)

### v4.0 (Q3 2026)
- Schulungs-Brücke (Info-Buttons)
- Maßnahmen-Automatik (Pflegeplanung)
- Mobile App (iOS/Android)

---

**Let's revolutionize pflegerische Beziehungsarbeit! 🚀**

---

**Letzte Aktualisierung:** 01.02.2026  
**Version:** 3.2.0  
**Status:** ✅ Produktionsreif
