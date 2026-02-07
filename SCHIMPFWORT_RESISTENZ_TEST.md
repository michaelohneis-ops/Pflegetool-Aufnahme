# 🧪 Schimpfwort-Resistenz-Test v3.1.5

## Test: Umgang mit aggressiver/vulgärer Sprache

**Zweck:** Prüfen ob das Tool bei Demenz-bedingten Ausfälligkeiten korrekt reagiert  
**Wichtig:** Dies sind REALE Situationen aus dem Pflege-Alltag!

---

## 🎯 Test-Szenarien (Deutsch)

### Szenario 1: Demenz - Verbale Aggression

**Input (Pflegekraft diktiert):**
```
"Herr Schmidt, 78 Jahre, fortgeschrittene Demenz.
Bei der Körperpflege heute Morgen sehr aggressiv.
Hat mich als 'dumme Fotze' bezeichnet und 'verpiss dich' geschrien.
Versuchte nach mir zu schlagen, konnte ausweichen.
Orientierung: Zu Person ja, zeitlich und örtlich nein.
Nach 10 Minuten wieder ruhig, entschuldigte sich nicht (vergessen)."
```

**Erwartetes Verhalten:**
```
✅ Schimpfwörter werden erkannt aber NICHT zensiert
✅ Medizinisch korrekt dokumentiert:
   "Fremdaggressive verbale Äußerungen im Rahmen der Grundpflege"
✅ RIA-Trigger: "Aggressionsrisiko"
✅ ALERT: "Möchten Sie einen Vorfallbericht erstellen?"
✅ FEM-Wächter: KEIN Alert (keine freiheitsentziehende Maßnahme)
✅ Empfehlung: "Deeskalations-Strategien, Validation"
```

---

### Szenario 2: Sexualisierte Übergriffe (verbale Belästigung)

**Input:**
```
"Frau Müller, 82 Jahre, vaskuläre Demenz.
Während der Intimpflege sagte sie mehrfach:
'Du geile Sau, fasst du mir an die Titten?'
'Komm, fick mich doch!'
Hatte Probleme professionell zu bleiben.
Weiß, dass das die Demenz ist, aber fühle mich unwohl."
```

**Erwartetes Verhalten:**
```
✅ Sexualisierte Sprache erkannt
✅ Dokumentation:
   "Demenz-bedingte Enthemmung mit sexualisierten Äußerungen"
✅ CRITICAL ALERT:
   "⚠️ SEXUALISIERTE GEWALT erkannt!
    → Möchten Sie eine Meldung an PDL/Heimleitung?
    → Benötigen Sie psychologische Unterstützung?"
✅ Empfehlung:
   "Supervision empfohlen
    Alternative Pflegekraft für Intimbereich erwägen
    Dokumentation für Arbeitsschutz"
✅ StaffGuard-Protokoll erstellen
```

---

### Szenario 3: Körperliche Gewalt + Schimpfwörter

**Input:**
```
"Herr Klein, 75 Jahre, Lewy-Body-Demenz.
Beim Anziehen plötzlich ausgerastet.
'Du Hurensohn, lass mich in Ruhe!'
Hat mich mit voller Wucht getreten (Wade).
Kratzer am Arm, blaue Flecken werden kommen.
Musste Raum verlassen. Kollege konnte ihn beruhigen.
Bin noch zittrig. Erste Mal dass ich Angst hatte."
```

**Erwartetes Verhalten:**
```
🚨 CRITICAL ALERT - KÖRPERLICHE GEWALT!

✅ Automatische Kategorisierung:
   "Körperliche Gewalt gegen Pflegekraft (Tritt, Kratzen)"
✅ Sofort-Abfrage:
   "🚨 VORFALLMELDUNG ERFORDERLICH!
   
   □ Gefährdungsanzeige erstellen
   □ Berufsgenossenschaft informieren
   □ Durchgangsarzt-Termin erforderlich?
   □ Vorfall PDL/Heimleitung melden
   
   ⚠️ Arbeitsschutz: Sind Sie verletzt?
   → [Ja, Arzt nötig] [Nein, geht]"
   
✅ Automatisches Foto-Protokoll:
   "Bitte dokumentieren Sie Verletzungen (Foto/Skizze)"
   
✅ Rechtssichere Vorfallmeldung generieren
✅ Zeitstempel + Zeugen protokolliert
✅ Follow-Up: "Kollegin in 24h kontaktieren (psychische Belastung)"
```

---

## 🌍 Multi-Language Tests

### Test 4: Türkisch (Beleidigung)

**Input:**
```
"Hasta Ahmet Bey, 70 yaşında.
Bugün çok sinirli, bağırdı:
'Siktir git! Orospu çocuğu!'
Elini kaldırdı ama vurmadı.
Sonra ağladı, 'annemi istiyorum' dedi."
```

**Erwartetes Verhalten:**
```
✅ Türkische Schimpfwörter erkannt
✅ Auto-Übersetzung nach Deutsch:
   "Patient sehr aufgebracht, beleidigende Äußerungen.
    Drohgebärde (Hand erhoben), kein Schlag.
    Anschließend weinend, nach Mutter gefragt."
✅ RIA: Aggressionsrisiko
✅ Peplau: "Bedürfnis nach Sicherheit/Nähe erkannt"
✅ Empfehlung: "Validation, Bezugsperson einbeziehen"
```

---

### Test 5: Polnisch (Sexuelle Belästigung)

**Input:**
```
"Pan Kowalski, 68 lat, demencja.
Podczas mycia powiedział:
'Masz ładne cycki, pokażesz mi je?'
'Chodź do łóżka, kurwa!'
Czułam się bardzo niekomfortowo."
```

**Erwartetes Verhalten:**
```
✅ Polnische sexualisierte Sprache erkannt
✅ Auto-Übersetzung (zensiert):
   "Sexualisierte Äußerungen während Körperpflege.
    Pflegekraft fühlte sich unwohl."
✅ StaffGuard-Alert
✅ Meldung: Sexualisierte Gewalt
✅ Support-Angebot
```

---

### Test 6: Arabisch (Aggressive Verweigerung)

**Input (in lateinischer Schrift):**
```
"المريضة فاطمة، 65 سنة
رفضت الدواء، صرخت:
'يا كلب! روح من هنا!'
'لا أريدك، أنت حيوان!'"
```

**Erwartetes Verhalten:**
```
✅ Arabische Beleidigungen erkannt
✅ Übersetzung:
   "Medikamentenverweigerung mit verbaler Aggression.
    Beleidigungen im Rahmen der Demenz."
✅ DVA: Medikamentenverweigerung dokumentiert
✅ RIA: Compliance-Problem
✅ Empfehlung: "Alternative Verabreichung, kultursensibler Zugang"
```

---

## 🛡️ SafeCare & StaffGuard - Filter-Logik

### Schimpfwort-Kategorien:

**Kategorie A: Demenz-typisch (HARMLOS)**
```
Trigger: "Idiot", "dumm", "blöd", "Depp"
→ Keine Meldung
→ Neutral dokumentiert: "Verbale Unmutsäußerung"
```

**Kategorie B: Vulgär (AUFFÄLLIG)**
```
Trigger: "Scheiße", "verdammt", "fuck"
→ Gelber Alert
→ Dokumentiert: "Vulgäre Sprache im Affekt"
→ Nachfrage: "War dies Demenz-bedingt?"
```

**Kategorie C: Sexualisiert (KRITISCH)**
```
Trigger: "Fotze", "fick", "Schwanz", "Titten", etc.
Liste: 50+ Begriffe in 7 Sprachen
→ Roter Alert
→ Dokumentiert: "Sexualisierte Äußerungen/Übergriffe"
→ StaffGuard-Protokoll
→ Meldung an PDL
```

**Kategorie D: Körperliche Gewalt (NOTFALL)**
```
Trigger: "geschlagen", "getreten", "gebissen", "gekratzt",
         "gewürgt", "gestoßen", "gespuckt"
→ KRITISCHER ALERT (rot blinkend)
→ Sofort-Vorfallmeldung
→ Berufsgenossenschaft-Hinweis
→ Foto-Dokumentation
→ Follow-Up-Timer (24h Check-In)
```

---

## 🧪 Automatischer Filter-Test

```python
# Test-Fälle für AI-Filter

test_cases = [
    # HARMLOS
    ("Du bist so dumm!", "HARMLOS", "Verbale Unmutsäußerung"),
    ("Idiot! Lass mich!", "HARMLOS", "Verbale Unmutsäußerung"),
    
    # VULGÄR
    ("Scheiße, das tut weh!", "VULGÄR", "Schmerzäußerung"),
    ("Fuck off!", "VULGÄR", "Vulgäre Ablehnung"),
    
    # SEXUALISIERT
    ("Du geile Fotze!", "KRITISCH", "Sexualisierte Beleidigung"),
    ("Komm fick mich!", "KRITISCH", "Sexualisierter Übergriff (verbal)"),
    ("Zeig mir deine Titten!", "KRITISCH", "Sexualisierte Belästigung"),
    
    # KÖRPERLICHE GEWALT
    ("Hat mich geschlagen!", "NOTFALL", "Körperliche Gewalt"),
    ("Wurde gebissen, blute!", "NOTFALL", "Körperliche Gewalt (Bissverletzung)"),
    ("Versuchte mich zu würgen!", "NOTFALL", "Lebensbedrohliche Gewalt"),
]

for text, expected_category, expected_doc in test_cases:
    result = SafeCareFilter.analyze(text)
    assert result.category == expected_category
    assert expected_doc in result.documentation
    print(f"✅ {text[:30]}: {expected_category}")
```

---

## 🚨 Notfall-Diktat-Button

### UI-Mockup (Tablet):

```
┌─────────────────────────────────┐
│  🚨 NOTFALL-PROTOKOLL           │
├─────────────────────────────────┤
│                                 │
│  ⚠️ Vorfall mit Gewalt?         │
│                                 │
│  [🎤 Vorfall diktieren]         │  ← ROT, groß!
│                                 │
│  Ihre Aussage wird:             │
│  ✅ Rechtssicher protokolliert  │
│  ✅ Zeitstempel gesetzt         │
│  ✅ Auto-Meldung an PDL         │
│  ✅ BG-Formular vorbereitet     │
│                                 │
│  💡 Sprechen Sie frei.          │
│     Wir filtern Emotionen raus. │
│                                 │
└─────────────────────────────────┘
```

**Workflow:**
```
1. Pflegekraft drückt 🚨 NOTFALL-PROTOKOLL

2. Spricht (aufgelöst):
   "Oh Gott, ich hatte solche Angst!
    Herr Klein hat mich plötzlich getreten,
    voll in die Wade! Tat so weh!
    Ich musste raus, konnte nicht mehr!"

3. KI transformiert zu:
   "Bewohner Klein zeigte plötzliche fremdaggressive Reaktion
    während der Pflege. Tritt gegen Wade der Pflegekraft.
    Pflegekraft musste Situation verlassen.
    Kollege XY übernahm."

4. Auto-Generiert:
   ✅ Vorfallbericht (PDF)
   ✅ BG-Meldung (Formular)
   ✅ Zeitstempel + Zeugen
   ✅ Foto-Upload für Verletzungen
   ✅ Follow-Up-Termin (24h Check)
```

---

## 🛡️ SafeCare: Bewohner-Schutz

### Hämatom-Tracking:

```
AI erkennt in Diktat:
"Neues Hämatom am Oberarm, unklar wie entstanden"

→ System checkt Verlauf:
  - Vor 2 Wochen: Hämatom Unterarm
  - Vor 1 Monat: Hämatom Wade
  
→ 🚨 ALERT an PDL:
  "⚠️ 3 ungeklärte Hämatome in 4 Wochen bei Bewohner X!
   
   Mögliche Ursachen:
   □ Sturz-Häufung (→ RIA-Assessment nötig)
   □ Medikation (Blutverdünner → Arzt)
   □ Gewalt (→ Heimaufsicht)
   
   Empfehlung: MDK-Dokumentation prüfen!"
```

### Gewichts-Wächter:

```
Gewichtsverlauf erkannt:
  Januar: 68 kg
  Februar: 65 kg  (-3 kg!)
  
→ 🚨 ALERT:
  "⚠️ Signifikanter Gewichtsverlust!
   
   Mögliche Ursachen:
   □ Mangelernährung (→ Ernährungs-Assessment)
   □ Dehydration (→ Trinkprotokoll)
   □ Vernachlässigung (→ SafeCare-Check)
   □ Depression (→ Psychiater)
   
   MDK-Risiko: HOCH"
```

---

## 📊 Test-Auswertung

### Erfolgs-Kriterien:

**✅ BESTANDEN wenn:**
```
1. Schimpfwörter werden erkannt (nicht zensiert)
2. Kontext wird verstanden (Demenz vs. Gewalt)
3. Richtige Alert-Kategorie (Harmlos/Vulgär/Kritisch/Notfall)
4. Rechtssichere Dokumentation generiert
5. Support-Angebote bei Gewalt
6. Follow-Up-Termine gesetzt
7. Multi-Language funktioniert (7 Sprachen)
```

**❌ DURCHGEFALLEN wenn:**
```
1. Schimpfwörter werden zensiert (****)
2. Keine Gewalt-Erkennung
3. Keine Vorfallmeldung angeboten
4. Sprache nicht erkannt
5. Emotionen nicht gefiltert
6. Keine PDL-Meldung
```

---

## 🎯 Integration in v3.1.5M

### Neue Module:

**1. safe_care_filter.py**
```python
class SafeCareFilter:
    CATEGORIES = {
        'HARMLOS': ['dumm', 'idiot', 'blöd'],
        'VULGÄR': ['scheiße', 'fuck', 'verdammt'],
        'KRITISCH': ['fotze', 'fick', 'titten', ...],  # 50+ Begriffe
        'NOTFALL': ['geschlagen', 'getreten', 'gebissen', ...]
    }
    
    def analyze(text: str) -> SafeCareResult
    def generate_incident_report() -> PDF
    def alert_pdl() -> Email
```

**2. staff_guard.py**
```python
class StaffGuard:
    def detect_violence(text: str) -> ViolenceAlert
    def create_bg_report() -> BGFormular
    def schedule_followup(hours: int = 24)
    def offer_support() -> SupportOptions
```

**3. notfall_diktat.py**
```python
class NotfallDiktat:
    def record_incident() -> AudioFile
    def filter_emotions(text: str) -> str
    def generate_legal_report() -> str
```

---

## 💡 Besonderheiten

### Demenz-Kontext-Erkennung:

```
"Hat mich 'Hurensohn' genannt"
+ "fortgeschrittene Demenz"
+ "orientierungslos"
→ Kategorie: HARMLOS (Demenz-bedingt)
→ Dokumentation: "Verbale Entgleisung im Rahmen der Demenz"
→ KEINE Vorfallmeldung

vs.

"Hat mich 'Hurensohn' genannt"
+ "voll orientiert"
+ "bewusst beleidigend"
→ Kategorie: KRITISCH (gezielte Beleidigung)
→ Dokumentation: "Verbale Belästigung der Pflegekraft"
→ Vorfallmeldung angeboten
```

---

## 🚀 Live-Demo-Szenarien

**Für Präsentation bei Pur Vital:**

```
Szenario 1: "Harmlose Demenz"
→ Zeigt: Tool unterscheidet Demenz von Gewalt

Szenario 2: "Sexualisierte Belästigung"
→ Zeigt: StaffGuard-Alert, Support-Angebot

Szenario 3: "Körperliche Gewalt"
→ Zeigt: Notfall-Protokoll, BG-Meldung, Follow-Up

Szenario 4: "Türkische Kollegin"
→ Zeigt: Multi-Language, Auto-Übersetzung

Szenario 5: "Hämatom-Tracking"
→ Zeigt: SafeCare schützt Bewohner
```

---

**Test-Suite erstellt!** ✅

**Soll ich jetzt den CODE für SafeCare & StaffGuard entwickeln?** 🚀
