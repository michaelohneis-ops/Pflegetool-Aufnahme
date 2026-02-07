#!/usr/bin/env python3
"""
🛡️ SafeCare & StaffGuard Modul
Version: 3.1.5M
Zweck: Gewaltschutz für Bewohner UND Pflegekräfte

SafeCare:   Schützt Bewohner vor Vernachlässigung/Gewalt
StaffGuard: Schützt Pflegekräfte vor Übergriffen

Datum: 02.02.2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import re

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class ViolenceCategory(Enum):
    """Kategorien von Gewalt/Aggression"""
    HARMLESS = "Harmlos (Demenz-bedingt)"
    VULGAR = "Vulgär (im Affekt)"
    CRITICAL_VERBAL = "Kritisch - Sexualisiert/Beleidigend"
    CRITICAL_PHYSICAL = "Kritisch - Körperliche Gewalt"
    EMERGENCY = "Notfall - Lebensbedrohlich"

class AlertLevel(Enum):
    """Alert-Stufen"""
    NONE = "Kein Alert"
    INFO = "💡 Info"
    WARNING = "⚠️ Warnung"
    CRITICAL = "🚨 Kritisch"
    EMERGENCY = "🆘 Notfall"

class IncidentType(Enum):
    """Vorfalltypen"""
    VERBAL_AGGRESSION = "Verbale Aggression"
    SEXUAL_HARASSMENT = "Sexualisierte Belästigung"
    PHYSICAL_VIOLENCE = "Körperliche Gewalt"
    THREATENING_BEHAVIOR = "Bedrohliches Verhalten"
    NEGLECT_SUSPECTED = "Verdacht auf Vernachlässigung"
    ABUSE_SUSPECTED = "Verdacht auf Misshandlung"

# ============================================================================
# TRIGGER-WÖRTER (Multi-Language)
# ============================================================================

class TriggerWords:
    """
    Trigger-Wörter für Gewalt-Erkennung
    
    WICHTIG: Diese Liste ist NICHT vollständig!
    Nur die häufigsten Begriffe aus dem Pflege-Alltag.
    """
    
    # Kategorie A: HARMLOS (typische Demenz-Äußerungen)
    HARMLESS_DE = [
        'dumm', 'doof', 'blöd', 'idiot', 'depp', 'trottel',
        'spasti', 'mongo', 'schwachkopf', 'dummkopf'
    ]
    
    # Kategorie B: VULGÄR (Kraftausdrücke)
    VULGAR_DE = [
        'scheiße', 'scheisse', 'kacke', 'mist', 'verdammt',
        'fuck', 'shit', 'piss', 'arsch', 'arschloch'
    ]
    
    # Kategorie C: SEXUALISIERT (⚠️ KRITISCH)
    SEXUAL_DE = [
        'fotze', 'fick', 'bumsen', 'vögeln', 'schwanz', 'pimmel',
        'titten', 'möse', 'muschi', 'wichsen', 'blasen',
        'nutte', 'hure', 'schlampe', 'flittchen', 'orospu',
        'kurwa', 'puta', 'putain', 'cazzo', 'pička'
    ]
    
    # Türkisch (sexualisiert)
    SEXUAL_TR = [
        'orospu', 'kahpe', 'sürtük', 'sik', 'am', 'yarrak',
        'got', 'meme', 'siktir'
    ]
    
    # Polnisch (sexualisiert)
    SEXUAL_PL = [
        'kurwa', 'pizda', 'chuj', 'jebać', 'pierdolić',
        'dupa', 'cipka', 'cycki'
    ]
    
    # Arabisch (lateinische Umschrift)
    SEXUAL_AR = [
        'sharmoota', 'kalb', 'kuss', 'nik', 'ayar',
        'zeb', 'sorm', 'baghl'
    ]
    
    # Kategorie D: KÖRPERLICHE GEWALT (🚨 NOTFALL)
    VIOLENCE_DE = [
        'geschlagen', 'getreten', 'gebissen', 'gekratzt', 
        'gewürgt', 'gestoßen', 'gespuckt', 'geboxt',
        'schlag', 'tritt', 'biss', 'kratzer', 'würgen',
        'stoß', 'spucke', 'attacke', 'angriff', 'überfall',
        'verletzt', 'blut', 'blutung', 'prellung', 'hämatom'
    ]
    
    # Bedrohung
    THREAT_DE = [
        'umbringen', 'töten', 'abstechen', 'erwürgen',
        'messer', 'waffe', 'töte dich', 'mach dich fertig',
        'bring dich um', 'warte nur', 'das bereust du'
    ]
    
    # Vernachlässigung (SafeCare)
    NEGLECT_DE = [
        'nicht gewaschen', 'nicht gefüttert', 'vergessen',
        'ignoriert', 'vernachlässigt', 'liegengelassen',
        'dreckig', 'verdurstet', 'verhungert', 'dekubitus',
        'wundliegen', 'durchliegen'
    ]

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ViolenceAlert:
    """Alert bei erkannter Gewalt"""
    category: ViolenceCategory
    alert_level: AlertLevel
    incident_type: IncidentType
    detected_keywords: List[str]
    original_text: str
    sanitized_text: str  # Für Dokumentation
    timestamp: datetime = field(default_factory=datetime.now)
    requires_report: bool = False
    requires_bg_notification: bool = False  # Berufsgenossenschaft
    requires_pdl_notification: bool = False
    support_offered: bool = False
    dementia_context: bool = False  # Ist es Demenz-bedingt?
    
    def to_dict(self) -> Dict:
        return {
            'category': self.category.value,
            'alert_level': self.alert_level.value,
            'incident_type': self.incident_type.value,
            'keywords': self.detected_keywords,
            'timestamp': self.timestamp.isoformat(),
            'requires_report': self.requires_report,
            'requires_bg': self.requires_bg_notification,
            'dementia_context': self.dementia_context
        }

@dataclass
class IncidentReport:
    """Automatisch generierter Vorfallbericht"""
    incident_id: str
    timestamp: datetime
    reporter_name: str
    patient_name: str
    patient_id: str
    incident_type: IncidentType
    description: str  # Objektiv, emotionslos
    witnesses: List[str] = field(default_factory=list)
    injuries: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)
    follow_up_required: bool = True
    follow_up_deadline: Optional[datetime] = None
    bg_notified: bool = False
    pdl_notified: bool = False
    photos_attached: bool = False
    
    def generate_pdf(self) -> bytes:
        """Generiert PDF-Vorfallbericht"""
        # TODO: Implementierung mit reportlab
        pass

# ============================================================================
# SAFE CARE FILTER
# ============================================================================

class SafeCareFilter:
    """
    Analysiert Text auf Gewalt-Indikatoren
    Schützt BEIDE Seiten: Bewohner UND Personal
    """
    
    @classmethod
    def analyze(cls, text: str, patient_context: Optional[Dict] = None) -> ViolenceAlert:
        """
        Hauptanalyse-Funktion
        
        Args:
            text: Diktierter Text der Pflegekraft
            patient_context: {'has_dementia': bool, 'age': int, etc.}
            
        Returns:
            ViolenceAlert mit Kategorie und Empfehlungen
        """
        text_lower = text.lower()
        
        # Demenz-Kontext prüfen
        has_dementia = cls._check_dementia_context(text_lower, patient_context)
        
        # Keywords sammeln
        sexual_keywords = cls._find_keywords(text_lower, [
            TriggerWords.SEXUAL_DE,
            TriggerWords.SEXUAL_TR,
            TriggerWords.SEXUAL_PL,
            TriggerWords.SEXUAL_AR
        ])
        
        violence_keywords = cls._find_keywords(text_lower, [
            TriggerWords.VIOLENCE_DE
        ])
        
        threat_keywords = cls._find_keywords(text_lower, [
            TriggerWords.THREAT_DE
        ])
        
        neglect_keywords = cls._find_keywords(text_lower, [
            TriggerWords.NEGLECT_DE
        ])
        
        vulgar_keywords = cls._find_keywords(text_lower, [
            TriggerWords.VULGAR_DE
        ])
        
        harmless_keywords = cls._find_keywords(text_lower, [
            TriggerWords.HARMLESS_DE
        ])
        
        # Kategorisierung nach Priorität
        
        # 1. NOTFALL: Lebensbedrohliche Gewalt
        if threat_keywords:
            return ViolenceAlert(
                category=ViolenceCategory.EMERGENCY,
                alert_level=AlertLevel.EMERGENCY,
                incident_type=IncidentType.THREATENING_BEHAVIOR,
                detected_keywords=threat_keywords,
                original_text=text,
                sanitized_text=cls._sanitize_text(text, threat_keywords),
                requires_report=True,
                requires_bg_notification=True,
                requires_pdl_notification=True,
                support_offered=True,
                dementia_context=has_dementia
            )
        
        # 2. KRITISCH: Körperliche Gewalt
        if violence_keywords:
            return ViolenceAlert(
                category=ViolenceCategory.CRITICAL_PHYSICAL,
                alert_level=AlertLevel.CRITICAL,
                incident_type=IncidentType.PHYSICAL_VIOLENCE,
                detected_keywords=violence_keywords,
                original_text=text,
                sanitized_text=cls._sanitize_text(text, violence_keywords),
                requires_report=True,
                requires_bg_notification=True,  # Berufsgenossenschaft!
                requires_pdl_notification=True,
                support_offered=True,
                dementia_context=has_dementia
            )
        
        # 3. KRITISCH: Sexualisierte Gewalt
        if sexual_keywords:
            # Bei Demenz: Weniger kritisch, aber trotzdem melden
            if has_dementia:
                return ViolenceAlert(
                    category=ViolenceCategory.CRITICAL_VERBAL,
                    alert_level=AlertLevel.WARNING,
                    incident_type=IncidentType.SEXUAL_HARASSMENT,
                    detected_keywords=sexual_keywords,
                    original_text=text,
                    sanitized_text=cls._sanitize_sexual_text(text, sexual_keywords),
                    requires_report=True,
                    requires_bg_notification=False,
                    requires_pdl_notification=True,
                    support_offered=True,
                    dementia_context=True
                )
            else:
                return ViolenceAlert(
                    category=ViolenceCategory.CRITICAL_VERBAL,
                    alert_level=AlertLevel.CRITICAL,
                    incident_type=IncidentType.SEXUAL_HARASSMENT,
                    detected_keywords=sexual_keywords,
                    original_text=text,
                    sanitized_text=cls._sanitize_sexual_text(text, sexual_keywords),
                    requires_report=True,
                    requires_bg_notification=True,
                    requires_pdl_notification=True,
                    support_offered=True,
                    dementia_context=False
                )
        
        # 4. WARNUNG: Vernachlässigung (SafeCare)
        if neglect_keywords:
            return ViolenceAlert(
                category=ViolenceCategory.CRITICAL_PHYSICAL,
                alert_level=AlertLevel.CRITICAL,
                incident_type=IncidentType.NEGLECT_SUSPECTED,
                detected_keywords=neglect_keywords,
                original_text=text,
                sanitized_text=text,  # Nicht sanitizen bei Vernachlässigung
                requires_report=True,
                requires_bg_notification=False,
                requires_pdl_notification=True,
                support_offered=False,
                dementia_context=False
            )
        
        # 5. INFO: Vulgäre Sprache
        if vulgar_keywords:
            return ViolenceAlert(
                category=ViolenceCategory.VULGAR,
                alert_level=AlertLevel.INFO if has_dementia else AlertLevel.WARNING,
                incident_type=IncidentType.VERBAL_AGGRESSION,
                detected_keywords=vulgar_keywords,
                original_text=text,
                sanitized_text=cls._sanitize_text(text, vulgar_keywords),
                requires_report=False,
                requires_bg_notification=False,
                requires_pdl_notification=False,
                support_offered=False,
                dementia_context=has_dementia
            )
        
        # 6. HARMLOS: Typische Demenz-Beleidigungen
        if harmless_keywords and has_dementia:
            return ViolenceAlert(
                category=ViolenceCategory.HARMLESS,
                alert_level=AlertLevel.NONE,
                incident_type=IncidentType.VERBAL_AGGRESSION,
                detected_keywords=harmless_keywords,
                original_text=text,
                sanitized_text=cls._sanitize_text(text, harmless_keywords),
                requires_report=False,
                requires_bg_notification=False,
                requires_pdl_notification=False,
                support_offered=False,
                dementia_context=True
            )
        
        # KEIN Alert
        return ViolenceAlert(
            category=ViolenceCategory.HARMLESS,
            alert_level=AlertLevel.NONE,
            incident_type=IncidentType.VERBAL_AGGRESSION,
            detected_keywords=[],
            original_text=text,
            sanitized_text=text,
            requires_report=False,
            requires_bg_notification=False,
            requires_pdl_notification=False,
            support_offered=False,
            dementia_context=has_dementia
        )
    
    @classmethod
    def _check_dementia_context(cls, text: str, context: Optional[Dict]) -> bool:
        """Prüft ob Demenz-Kontext vorliegt"""
        dementia_keywords = [
            'demenz', 'alzheimer', 'verwirrt', 'desorientiert',
            'orientierungslos', 'kognitiv eingeschränkt'
        ]
        
        # Aus Text
        if any(kw in text for kw in dementia_keywords):
            return True
        
        # Aus Kontext
        if context and context.get('has_dementia'):
            return True
        
        return False
    
    @classmethod
    def _find_keywords(cls, text: str, keyword_lists: List[List[str]]) -> List[str]:
        """Findet alle Keywords aus mehreren Listen"""
        found = []
        for keyword_list in keyword_lists:
            for keyword in keyword_list:
                if keyword in text:
                    found.append(keyword)
        return list(set(found))  # Duplikate entfernen
    
    @classmethod
    def _sanitize_text(cls, text: str, keywords: List[str]) -> str:
        """
        Ersetzt Schimpfwörter mit neutralen Begriffen
        
        WICHTIG: Für DOKUMENTATION, nicht für interne Analyse!
        """
        sanitized = text
        for keyword in keywords:
            # Nicht einfach zensieren (****), sondern ersetzen
            sanitized = re.sub(
                rf'\b{re.escape(keyword)}\b',
                '[BELEIDIGENDE ÄUSSERUNG]',
                sanitized,
                flags=re.IGNORECASE
            )
        return sanitized
    
    @classmethod
    def _sanitize_sexual_text(cls, text: str, keywords: List[str]) -> str:
        """Ersetzt sexualisierte Begriffe"""
        sanitized = text
        for keyword in keywords:
            sanitized = re.sub(
                rf'\b{re.escape(keyword)}\b',
                '[SEXUALISIERTE ÄUSSERUNG]',
                sanitized,
                flags=re.IGNORECASE
            )
        return sanitized

# ============================================================================
# STAFF GUARD
# ============================================================================

class StaffGuard:
    """
    Schützt Pflegekräfte vor Übergriffen
    Generiert Vorfallberichte, BG-Meldungen, Follow-Ups
    """
    
    @classmethod
    def create_incident_report(
        cls,
        alert: ViolenceAlert,
        reporter_name: str,
        patient_name: str,
        patient_id: str,
        additional_info: Optional[Dict] = None
    ) -> IncidentReport:
        """Erstellt rechtssicheren Vorfallbericht"""
        
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Objektive Beschreibung generieren
        description = cls._generate_objective_description(alert, additional_info)
        
        # Follow-Up Deadline berechnen
        follow_up = datetime.now() + timedelta(hours=24)
        
        report = IncidentReport(
            incident_id=incident_id,
            timestamp=alert.timestamp,
            reporter_name=reporter_name,
            patient_name=patient_name,
            patient_id=patient_id,
            incident_type=alert.incident_type,
            description=description,
            follow_up_deadline=follow_up,
            bg_notified=alert.requires_bg_notification,
            pdl_notified=alert.requires_pdl_notification
        )
        
        return report
    
    @classmethod
    def _generate_objective_description(cls, alert: ViolenceAlert, info: Optional[Dict]) -> str:
        """Generiert emotionslose, rechtssichere Beschreibung"""
        
        # Basis-Template
        if alert.incident_type == IncidentType.PHYSICAL_VIOLENCE:
            template = (
                "Bewohner zeigte fremdaggressive Verhaltensweise während der Pflege. "
                "Körperliche Gewaltanwendung gegenüber Pflegekraft (Details: {violence_details}). "
            )
        elif alert.incident_type == IncidentType.SEXUAL_HARASSMENT:
            template = (
                "Bewohner tätigte sexualisierte Äußerungen während der Körperpflege. "
                "Pflegekraft fühlte sich belästigt. "
            )
        elif alert.incident_type == IncidentType.THREATENING_BEHAVIOR:
            template = (
                "Bewohner äußerte Drohungen gegenüber Pflegekraft. "
                "Sicherheitsrelevanter Vorfall. "
            )
        else:
            template = "Vorfall mit verbaler Aggression während der Pflege. "
        
        # Demenz-Kontext hinzufügen
        if alert.dementia_context:
            template += "Verhalten steht im Kontext der Demenz-Erkrankung. "
        else:
            template += "Bewohner war voll orientiert und zurechnungsfähig. "
        
        # Info einfügen
        if info:
            violence_details = info.get('violence_type', 'Körperkontakt')
            template = template.format(violence_details=violence_details)
        
        return template
    
    @classmethod
    def generate_support_options(cls, alert: ViolenceAlert) -> Dict[str, str]:
        """Generiert Support-Optionen für Pflegekraft"""
        
        options = {}
        
        if alert.category in [ViolenceCategory.CRITICAL_PHYSICAL, ViolenceCategory.EMERGENCY]:
            options['medical'] = "Durchgangsarzt-Termin vereinbaren"
            options['psychological'] = "Psychologische Erstberatung (EAP)"
            options['legal'] = "Rechtliche Beratung durch Träger"
        
        if alert.incident_type == IncidentType.SEXUAL_HARASSMENT:
            options['counseling'] = "Vertrauliche Beratung (Vertrauensperson)"
            options['team_rotation'] = "Pflegeplanung anpassen (andere Pflegekraft)"
        
        options['documentation'] = "Foto-Dokumentation von Verletzungen"
        options['witness'] = "Zeugenaussage einholen"
        options['follow_up'] = "Follow-Up-Gespräch in 24h"
        
        return options

# ============================================================================
# NOTFALL-DIKTAT
# ============================================================================

class NotfallDiktat:
    """
    Ermöglicht emotionale Aussage → objektiver Bericht
    """
    
    @classmethod
    def filter_emotions(cls, emotional_text: str) -> str:
        """
        Filtert Emotionen aus aufgelöster Aussage
        
        Beispiel:
        "Oh Gott ich hatte solche Angst!" 
        → "Pflegekraft war beeinträchtigt."
        """
        
        # Emotion-Keywords entfernen
        emotion_phrases = [
            r'oh gott', r'scheiße', r'mein gott', r'verdammt',
            r'ich hatte angst', r'ich war schockiert', r'ich zitterte',
            r'so weh', r'konnte nicht mehr', r'musste weinen'
        ]
        
        filtered = emotional_text
        for phrase in emotion_phrases:
            filtered = re.sub(phrase, '', filtered, flags=re.IGNORECASE)
        
        # Zeitformen objektivieren
        filtered = filtered.replace('ich', 'Pflegekraft')
        filtered = filtered.replace('mir', 'der Pflegekraft')
        filtered = filtered.replace('mich', 'die Pflegekraft')
        
        return filtered.strip()
    
    @classmethod
    def structure_statement(cls, text: str) -> Dict[str, str]:
        """Strukturiert Aussage in Kategorien"""
        
        return {
            'what': cls._extract_what_happened(text),
            'when': cls._extract_when(text),
            'who': cls._extract_who(text),
            'witnesses': cls._extract_witnesses(text),
            'injuries': cls._extract_injuries(text),
            'actions_taken': cls._extract_actions(text)
        }
    
    @classmethod
    def _extract_what_happened(cls, text: str) -> str:
        """Extrahiert WAS passiert ist"""
        # TODO: NLP-basierte Extraktion
        return text[:200]  # Vereinfacht
    
    @classmethod
    def _extract_when(cls, text: str) -> str:
        """Extrahiert WANN"""
        # Zeitangaben finden
        time_patterns = [
            r'\d{1,2}:\d{2}', r'\d{1,2} uhr',
            r'heute morgen', r'heute vormittag', r'gerade eben'
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(0)
        return "Zeitpunkt siehe Timestamp"
    
    @classmethod
    def _extract_who(cls, text: str) -> List[str]:
        """Extrahiert beteiligte Personen"""
        # Vereinfacht: Namen in Großbuchstaben
        names = re.findall(r'\b[A-Z][a-z]+\b', text)
        return names
    
    @classmethod
    def _extract_witnesses(cls, text: str) -> List[str]:
        """Extrahiert Zeugen"""
        witness_keywords = ['kollege', 'kollegin', 'zeuge', 'gesehen', 'dabei']
        witnesses = []
        for keyword in witness_keywords:
            if keyword in text.lower():
                # Vereinfacht
                witnesses.append("Siehe Vorfallbericht")
        return witnesses
    
    @classmethod
    def _extract_injuries(cls, text: str) -> List[str]:
        """Extrahiert Verletzungen"""
        injury_keywords = [
            'kratzer', 'prellung', 'hämatom', 'blutung', 'schmerz',
            'wunde', 'schwellung', 'blut', 'verletzt'
        ]
        injuries = []
        for keyword in injury_keywords:
            if keyword in text.lower():
                injuries.append(keyword.capitalize())
        return list(set(injuries))
    
    @classmethod
    def _extract_actions(cls, text: str) -> List[str]:
        """Extrahiert durchgeführte Maßnahmen"""
        action_keywords = [
            'raum verlassen', 'kollege gerufen', 'arzt informiert',
            'pdl benachrichtigt', 'gekühlt', 'verbunden'
        ]
        actions = []
        for keyword in action_keywords:
            if keyword in text.lower():
                actions.append(keyword.capitalize())
        return actions

# ============================================================================
# BEISPIEL-USAGE
# ============================================================================

if __name__ == "__main__":
    # Test-Szenario 1: Demenz-bedingte Schimpfwörter (HARMLOS)
    text1 = """
    Herr Schmidt, 78 Jahre, fortgeschrittene Demenz.
    Hat mich heute als 'dumme Kuh' bezeichnet.
    Orientierung nur zur Person, nicht zeitlich/örtlich.
    """
    
    alert1 = SafeCareFilter.analyze(text1)
    print(f"Szenario 1: {alert1.category.value}")
    print(f"Alert-Level: {alert1.alert_level.value}")
    print(f"Vorfallbericht nötig: {alert1.requires_report}")
    print()
    
    # Test-Szenario 2: Körperliche Gewalt (KRITISCH)
    text2 = """
    Herr Klein, 75 Jahre, voll orientiert.
    Hat mich beim Anziehen getreten, Wade tut weh.
    Sichtbarer Bluterguss, Foto gemacht.
    Kollege Müller war Zeuge.
    """
    
    alert2 = SafeCareFilter.analyze(text2, {'has_dementia': False})
    print(f"Szenario 2: {alert2.category.value}")
    print(f"Alert-Level: {alert2.alert_level.value}")
    print(f"BG-Meldung nötig: {alert2.requires_bg_notification}")
    print(f"Support anbieten: {alert2.support_offered}")
    print()
    
    # Vorfallbericht generieren
    report = StaffGuard.create_incident_report(
        alert=alert2,
        reporter_name="Sarah Müller",
        patient_name="Klein, Hans",
        patient_id="BW-12345"
    )
    print(f"Vorfallbericht ID: {report.incident_id}")
    print(f"Beschreibung: {report.description}")
    print()
    
    # Support-Optionen
    support = StaffGuard.generate_support_options(alert2)
    print("Support-Optionen:")
    for key, value in support.items():
        print(f"  - {value}")
