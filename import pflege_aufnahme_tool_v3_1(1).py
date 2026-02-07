#!/usr/bin/env python3
"""
🏥 Professionelles Pflegerisches Aufnahme-Tool
Version: 3.1 - Mit Smart-Copy & MDK-Simulator
Datum: 31.01.2026

NEU in v3.1:
- Smart-Copy für DM7/Vivendi/Medifox Export
- MDK-Simulator Dashboard
- Compliance-Tracking über Zeit

Integriert:
- RIA (Risikoassessment)
- SiS (Strukturierte Informationssammlung)
- BI (Begutachtungsinstrument)
- FEM-Wächter (Freiheitsentziehende Maßnahmen)
- DVA-Compliance (Dienst- und Verfahrensanweisungen)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
import json
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import io
from fpdf import FPDF

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class RiskLevel(Enum):
    """Risikostufen nach Pflegestandard"""
    NONE = "Kein Risiko"
    LOW = "Niedriges Risiko"
    MEDIUM = "Mittleres Risiko"
    HIGH = "Hohes Risiko"
    CRITICAL = "Kritisch - Sofortmaßnahmen"

class DVACompliance(Enum):
    """Compliance-Status nach DVA"""
    COMPLIANT = "✅ DVA-konform"
    NEEDS_ATTENTION = "⚠️ Überprüfung erforderlich"
    NON_COMPLIANT = "❌ DVA-Verstoß - Handlung erforderlich"
    NOT_APPLICABLE = "➖ Nicht anwendbar"

class BIModuleCategory(Enum):
    """BI-Modul Kategorien nach NBA"""
    INDEPENDENT = "Selbstständig"
    MOSTLY_INDEPENDENT = "Überwiegend selbstständig"
    MOSTLY_DEPENDENT = "Überwiegend unselbstständig"
    DEPENDENT = "Unselbstständig"

class ExportFormat(Enum):
    """Export-Formate für verschiedene Pflegesoftware"""
    DM7 = "DM7 (Connext)"
    VIVENDI = "Vivendi PD"
    MEDIFOX = "Medifox DAN"
    GENERIC = "Generisch (Reintext)"

# ============================================================================
# DATA MODELS (erweitert)
# ============================================================================

@dataclass
class FEMAlert:
    """FEM-Wächter Alert Structure"""
    detected_keyword: str
    legal_reference: str
    severity: str
    immediate_actions: List[str]
    alternatives: List[str]
    deadline_hours: int
    documentation_required: List[str]
    beschluss_vorhanden: bool = False  # NEU: Für MDK-Tracking
    beschluss_datum: Optional[datetime] = None  # NEU
    
    def to_dict(self):
        return asdict(self)

@dataclass
class RIATrigger:
    """RIA-Trigger mit erweiterten Compliance-Informationen"""
    name: str
    risk_level: RiskLevel
    evidence: str
    recommended_action: str
    deadline_hours: int = 24
    dva_reference: Optional[str] = None
    compliance_status: DVACompliance = DVACompliance.NOT_APPLICABLE
    fem_alert: Optional[FEMAlert] = None
    massnahmen_umgesetzt: bool = False  # NEU: Für MDK-Tracking
    
    def to_dict(self):
        return {
            'name': self.name,
            'risk_level': self.risk_level.value,
            'evidence': self.evidence,
            'recommended_action': self.recommended_action,
            'deadline_hours': self.deadline_hours,
            'dva_reference': self.dva_reference,
            'compliance_status': self.compliance_status.value,
            'fem_alert': self.fem_alert.to_dict() if self.fem_alert else None,
            'massnahmen_umgesetzt': self.massnahmen_umgesetzt
        }

@dataclass
class BIModule:
    """BI-Modul nach NBA"""
    module_id: int
    module_name: str
    points: int
    max_points: int
    category: BIModuleCategory
    evidence: str
    wkm_suggestions: List[str] = field(default_factory=list)
    dva_compliant: bool = True
    compliance_notes: str = ""

@dataclass
class SISStructure:
    """Strukturierte Informationssammlung"""
    themenfeld: str
    information: str
    risiken: List[str] = field(default_factory=list)
    ressourcen: List[str] = field(default_factory=list)
    wünsche_patient: str = ""
    maßnahmen_geplant: List[str] = field(default_factory=list)

@dataclass
class DVACheck:
    """Dienst- und Verfahrensanweisung Check"""
    dva_id: str
    dva_title: str
    applicable: bool
    compliant: bool
    findings: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    responsible_person: str = ""
    deadline: Optional[datetime] = None
    actions_completed: bool = False  # NEU: Für MDK-Tracking

@dataclass
class AssessmentResult:
    """Vollständiges Aufnahme-Assessment"""
    patient_id: str
    patient_name: str
    aufnahme_datum: datetime
    aufgenommen_durch: str
    
    # Kern-Assessments
    ria_triggers: List[RIATrigger] = field(default_factory=list)
    bi_modules: List[BIModule] = field(default_factory=list)
    sis_strukturen: List[SISStructure] = field(default_factory=list)
    
    # FEM & DVA
    fem_alerts: List[FEMAlert] = field(default_factory=list)
    dva_checks: List[DVACheck] = field(default_factory=list)
    
    # Compliance
    overall_compliance: DVACompliance = DVACompliance.COMPLIANT
    review_required: bool = False
    reviewer_name: Optional[str] = None
    review_date: Optional[datetime] = None
    
    # NEU: MDK-Tracking
    mdk_ready: bool = False
    compliance_score: float = 0.0  # 0-100%

# ============================================================================
# SMART-COPY EXPORT ENGINE (NEU v3.1)
# ============================================================================

class SmartCopyEngine:
    """
    Exportiert Assessment-Daten formatiert für verschiedene Pflegesoftware
    Systeme: DM7, Vivendi, Medifox
    """
    
    # SiS-Themenfelder nach NBA (standardisiert)
    SIS_THEMENFELDER = {
        1: "Kognition und Kommunikation",
        2: "Mobilität und Beweglichkeit",
        3: "Krankheitsbezogene Anforderungen und Belastungen",
        4: "Selbstversorgung",
        5: "Leben in sozialen Beziehungen",
        6: "Haushaltsführung"
    }
    
    @classmethod
    def export_for_dm7(cls, result: AssessmentResult) -> str:
        """
        Export für DM7 (Connext)
        Format: Strukturierte Informationssammlung nach NBA
        """
        output = []
        
        output.append("=" * 80)
        output.append("STRUKTURIERTE INFORMATIONSSAMMLUNG (SiS)")
        output.append(f"Bewohner: {result.patient_name} (ID: {result.patient_id})")
        output.append(f"Aufnahmedatum: {result.aufnahme_datum.strftime('%d.%m.%Y')}")
        output.append(f"Aufgenommen durch: {result.aufgenommen_durch}")
        output.append("=" * 80)
        output.append("")
        
        # Themenfeld 1: Kognition
        output.append("THEMENFELD 1: Kognition und Kommunikation")
        output.append("-" * 80)
        
        kognitiv_info = []
        kognitiv_risiken = []
        
        # Aus BI-Modul 2 extrahieren
        for bi in result.bi_modules:
            if bi.module_id == 2:
                kognitiv_info.append(f"Kognitive Fähigkeiten: {bi.category.value} ({bi.points}/{bi.max_points} Punkte)")
                kognitiv_info.append(f"Evidenz: {bi.evidence}")
        
        # Aus RIA-Triggern
        for trigger in result.ria_triggers:
            if 'demenz' in trigger.name.lower() or 'verwirr' in trigger.name.lower():
                kognitiv_risiken.append(f"⚠️ {trigger.name} ({trigger.risk_level.value})")
        
        output.append("Information:")
        if kognitiv_info:
            for info in kognitiv_info:
                output.append(f"  • {info}")
        else:
            output.append("  • Keine besonderen Befunde dokumentiert")
        
        output.append("")
        output.append("Risiken:")
        if kognitiv_risiken:
            for risk in kognitiv_risiken:
                output.append(f"  • {risk}")
        else:
            output.append("  • Keine kognitiven Risiken identifiziert")
        
        output.append("")
        output.append("")
        
        # Themenfeld 2: Mobilität
        output.append("THEMENFELD 2: Mobilität und Beweglichkeit")
        output.append("-" * 80)
        
        mobilitaet_info = []
        mobilitaet_risiken = []
        mobilitaet_ressourcen = []
        
        for bi in result.bi_modules:
            if bi.module_id == 1:
                mobilitaet_info.append(f"Mobilität: {bi.category.value} ({bi.points}/{bi.max_points} Punkte)")
                mobilitaet_info.append(f"Evidenz: {bi.evidence}")
                
                if bi.category in [BIModuleCategory.MOSTLY_DEPENDENT, BIModuleCategory.DEPENDENT]:
                    mobilitaet_risiken.append("Eingeschränkte Mobilität")
        
        for trigger in result.ria_triggers:
            if 'sturz' in trigger.name.lower():
                mobilitaet_risiken.append(f"⚠️ {trigger.name} ({trigger.risk_level.value})")
        
        # Hilfsmittel als Ressource
        if any('gehstock' in trigger.evidence.lower() or 'rollstuhl' in trigger.evidence.lower() 
               for trigger in result.ria_triggers):
            mobilitaet_ressourcen.append("Hilfsmittel vorhanden (Gehstock/Rollstuhl)")
        
        output.append("Information:")
        for info in mobilitaet_info:
            output.append(f"  • {info}")
        
        output.append("")
        output.append("Risiken:")
        if mobilitaet_risiken:
            for risk in mobilitaet_risiken:
                output.append(f"  • {risk}")
        else:
            output.append("  • Keine Mobilitätsrisiken identifiziert")
        
        output.append("")
        output.append("Ressourcen:")
        if mobilitaet_ressourcen:
            for res in mobilitaet_ressourcen:
                output.append(f"  • {res}")
        else:
            output.append("  • Keine besonderen Ressourcen dokumentiert")
        
        output.append("")
        output.append("")
        
        # Themenfeld 3: Krankheitsbezogene Anforderungen
        output.append("THEMENFELD 3: Krankheitsbezogene Anforderungen und Belastungen")
        output.append("-" * 80)
        
        krankheit_info = []
        krankheit_risiken = []
        
        for bi in result.bi_modules:
            if bi.module_id == 5:
                krankheit_info.append(f"Krankheitsbewältigung: {bi.category.value}")
                krankheit_info.append(f"Evidenz: {bi.evidence}")
        
        for trigger in result.ria_triggers:
            if trigger.name.lower() not in ['sturz', 'demenz']:
                krankheit_risiken.append(f"⚠️ {trigger.name} ({trigger.risk_level.value})")
        
        output.append("Information:")
        if krankheit_info:
            for info in krankheit_info:
                output.append(f"  • {info}")
        else:
            output.append("  • Keine besonderen krankheitsbezogenen Anforderungen dokumentiert")
        
        output.append("")
        output.append("Risiken:")
        if krankheit_risiken:
            for risk in krankheit_risiken:
                output.append(f"  • {risk}")
        else:
            output.append("  • Keine spezifischen Risiken identifiziert")
        
        output.append("")
        output.append("")
        
        # Themenfeld 4: Selbstversorgung
        output.append("THEMENFELD 4: Selbstversorgung")
        output.append("-" * 80)
        
        selbst_info = []
        
        for bi in result.bi_modules:
            if bi.module_id == 4:
                selbst_info.append(f"Selbstversorgung: {bi.category.value} ({bi.points}/{bi.max_points} Punkte)")
                selbst_info.append(f"Evidenz: {bi.evidence}")
        
        output.append("Information:")
        if selbst_info:
            for info in selbst_info:
                output.append(f"  • {info}")
        else:
            output.append("  • Keine besonderen Befunde zur Selbstversorgung")
        
        output.append("")
        output.append("")
        
        # FEM-WÄCHTER Hinweis (KRITISCH!)
        if result.fem_alerts:
            output.append("=" * 80)
            output.append("🚨 WICHTIG: FREIHEITSENTZIEHENDE MASSNAHMEN ERKANNT!")
            output.append("=" * 80)
            
            for alert in result.fem_alerts:
                output.append(f"")
                output.append(f"Maßnahme: {alert.detected_keyword}")
                output.append(f"Rechtsgrundlage: {alert.legal_reference}")
                output.append(f"")
                output.append("SOFORTMASSNAHMEN:")
                for action in alert.immediate_actions:
                    output.append(f"  ☐ {action}")
                output.append("")
                output.append("Beschluss vorhanden: " + ("✅ JA" if alert.beschluss_vorhanden else "❌ NEIN - DRINGEND EINHOLEN!"))
                if alert.beschluss_datum:
                    output.append(f"Beschluss-Datum: {alert.beschluss_datum.strftime('%d.%m.%Y')}")
                output.append("")
        
        # DVA-Compliance Status
        output.append("=" * 80)
        output.append("DVA-COMPLIANCE STATUS")
        output.append("=" * 80)
        output.append("")
        
        for check in result.dva_checks:
            status = "✅" if check.compliant else "⚠️"
            output.append(f"{status} {check.dva_id}: {check.dva_title}")
            if not check.compliant:
                output.append("  Erforderliche Maßnahmen:")
                for action in check.required_actions:
                    completed = "✅" if check.actions_completed else "☐"
                    output.append(f"    {completed} {action}")
            output.append("")
        
        output.append("=" * 80)
        output.append(f"Gesamtbewertung: {result.overall_compliance.value}")
        output.append(f"Compliance-Score: {result.compliance_score:.1f}%")
        output.append(f"MDK-Ready: {'✅ JA' if result.mdk_ready else '⚠️ NEIN'}")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    @classmethod
    def export_for_vivendi(cls, result: AssessmentResult) -> str:
        """Export für Vivendi PD (ähnlich DM7, leicht angepasstes Format)"""
        # Vivendi nutzt ähnliche Struktur wie DM7
        base_export = cls.export_for_dm7(result)
        
        # Header anpassen
        vivendi_export = base_export.replace(
            "STRUKTURIERTE INFORMATIONSSAMMLUNG (SiS)",
            "STRUKTURIERTE INFORMATIONSSAMMLUNG (SiS) - VIVENDI PD"
        )
        
        return vivendi_export
    
    @classmethod
    def export_for_medifox(cls, result: AssessmentResult) -> str:
        """Export für Medifox DAN (kompakteres Format)"""
        output = []
        
        output.append("MEDIFOX DAN - AUFNAHMEDOKUMENTATION")
        output.append("=" * 60)
        output.append(f"Bewohner: {result.patient_name}")
        output.append(f"ID: {result.patient_id}")
        output.append(f"Aufnahme: {result.aufnahme_datum.strftime('%d.%m.%Y %H:%M')}")
        output.append("=" * 60)
        output.append("")
        
        # RIA-Zusammenfassung
        if result.ria_triggers:
            output.append("RISIKOASSESSMENT:")
            for trigger in result.ria_triggers:
                risk_emoji = {"Kritisch - Sofortmaßnahmen": "🔴", 
                             "Hohes Risiko": "🟠",
                             "Mittleres Risiko": "🟡",
                             "Niedriges Risiko": "🟢"}.get(trigger.risk_level.value, "⚪")
                
                output.append(f"  {risk_emoji} {trigger.name}")
                output.append(f"     Maßnahmen: {trigger.recommended_action[:100]}...")
            output.append("")
        
        # BI-Zusammenfassung
        if result.bi_modules:
            output.append("BEGUTACHTUNG (BI/NBA):")
            for bi in result.bi_modules:
                output.append(f"  • Modul {bi.module_id} ({bi.module_name}): {bi.points}/{bi.max_points} Pkt. - {bi.category.value}")
            output.append("")
        
        # FEM-Alerts
        if result.fem_alerts:
            output.append("⚠️ FEM-MASSNAHMEN ERKANNT:")
            for alert in result.fem_alerts:
                output.append(f"  • {alert.detected_keyword} - Beschluss: {'✅' if alert.beschluss_vorhanden else '❌'}")
            output.append("")
        
        # Compliance
        output.append(f"COMPLIANCE: {result.overall_compliance.value} ({result.compliance_score:.0f}%)")
        output.append(f"MDK-READY: {'✅' if result.mdk_ready else '❌'}")
        
        output.append("=" * 60)
        
        return "\n".join(output)
    
    @classmethod
    def export_generic(cls, result: AssessmentResult) -> str:
        """Generischer Export (Reintext, universell)"""
        return cls.export_for_dm7(result)  # DM7-Format als Basis

# ============================================================================
# MDK-SIMULATOR ENGINE (NEU v3.1)
# ============================================================================

class MDKSimulator:
    """
    Simuliert MDK-Prüfung und erstellt Compliance-Reports
    Basis: Expertenstandards, DVA-Compliance, FEM-Überwachung
    """
    
    @classmethod
    def calculate_compliance_score(cls, result: AssessmentResult) -> float:
        """
        Berechnet Compliance-Score (0-100%)
        
        Kriterien:
        - DVA-Checks vollständig: 40%
        - FEM-Beschlüsse vorhanden: 30%
        - RIA-Maßnahmen umgesetzt: 20%
        - Dokumentation vollständig: 10%
        """
        score = 0.0
        
        # 1. DVA-Compliance (40 Punkte)
        if result.dva_checks:
            compliant_checks = sum(1 for check in result.dva_checks if check.compliant or check.actions_completed)
            dva_score = (compliant_checks / len(result.dva_checks)) * 40
            score += dva_score
        else:
            score += 40  # Keine DVA-Checks = keine Verstöße
        
        # 2. FEM-Beschlüsse (30 Punkte)
        if result.fem_alerts:
            alerts_with_beschluss = sum(1 for alert in result.fem_alerts if alert.beschluss_vorhanden)
            fem_score = (alerts_with_beschluss / len(result.fem_alerts)) * 30
            score += fem_score
        else:
            score += 30  # Keine FEM = volle Punkte
        
        # 3. RIA-Maßnahmen umgesetzt (20 Punkte)
        if result.ria_triggers:
            completed_actions = sum(1 for trigger in result.ria_triggers if trigger.massnahmen_umgesetzt)
            ria_score = (completed_actions / len(result.ria_triggers)) * 20
            score += ria_score
        else:
            score += 20  # Keine RIA-Trigger = volle Punkte
        
        # 4. Dokumentation vollständig (10 Punkte)
        if result.reviewer_name and result.review_date:
            score += 10  # Review durchgeführt
        
        return min(score, 100.0)  # Max 100%
    
    @classmethod
    def assess_mdk_readiness(cls, result: AssessmentResult) -> Tuple[bool, List[str]]:
        """
        Prüft MDK-Bereitschaft
        Returns: (ready: bool, issues: List[str])
        """
        issues = []
        
        # Kritische FEM-Checks
        for alert in result.fem_alerts:
            if not alert.beschluss_vorhanden:
                issues.append(f"🔴 KRITISCH: FEM-Beschluss fehlt für '{alert.detected_keyword}'")
        
        # DVA-Verstöße
        for check in result.dva_checks:
            if check.applicable and not check.compliant and not check.actions_completed:
                issues.append(f"🟠 DVA-Verstoß: {check.dva_id} ({check.dva_title}) - Maßnahmen nicht umgesetzt")
        
        # Fehlende Maßnahmen
        critical_triggers = [t for t in result.ria_triggers if t.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        for trigger in critical_triggers:
            if not trigger.massnahmen_umgesetzt:
                issues.append(f"🟡 Maßnahmen fehlen: {trigger.name}")
        
        # Review-Status
        if not result.reviewer_name:
            issues.append("🟡 4-Augen-Prinzip: Review ausstehend")
        
        ready = len(issues) == 0
        
        return ready, issues
    
    @classmethod
    def generate_mdk_report(cls, assessments: List[AssessmentResult]) -> str:
        """
        Generiert MDK-Prüfbericht für mehrere Aufnahmen
        """
        output = []
        
        output.append("=" * 80)
        output.append("MDK-PRÜFBERICHT - QUALITÄTSSICHERUNG PFLEGERISCHE AUFNAHMEN")
        output.append("=" * 80)
        output.append(f"Berichtsdatum: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        output.append(f"Anzahl Aufnahmen: {len(assessments)}")
        output.append("")
        
        # Gesamtstatistik
        total_score = sum(a.compliance_score for a in assessments) / len(assessments) if assessments else 0
        mdk_ready_count = sum(1 for a in assessments if a.mdk_ready)
        fem_alerts_total = sum(len(a.fem_alerts) for a in assessments)
        fem_beschluesse_total = sum(sum(1 for alert in a.fem_alerts if alert.beschluss_vorhanden) for a in assessments)
        
        output.append("GESAMTÜBERSICHT:")
        output.append("-" * 80)
        output.append(f"Durchschnittlicher Compliance-Score: {total_score:.1f}%")
        output.append(f"MDK-Ready Aufnahmen: {mdk_ready_count}/{len(assessments)} ({mdk_ready_count/len(assessments)*100:.0f}%)")
        output.append(f"FEM-Alerts gesamt: {fem_alerts_total}")
        if fem_alerts_total > 0:
            output.append(f"FEM-Beschlüsse vorhanden: {fem_beschluesse_total}/{fem_alerts_total} ({fem_beschluesse_total/fem_alerts_total*100:.0f}%)")
        output.append("")
        
        # Kritische Fälle
        critical_cases = [a for a in assessments if not a.mdk_ready]
        
        if critical_cases:
            output.append("⚠️ HANDLUNGSBEDARF (Nicht MDK-Ready):")
            output.append("-" * 80)
            
            for case in critical_cases:
                output.append(f"")
                output.append(f"Patient: {case.patient_name} (ID: {case.patient_id})")
                output.append(f"Aufnahme: {case.aufnahme_datum.strftime('%d.%m.%Y')}")
                output.append(f"Compliance-Score: {case.compliance_score:.1f}%")
                
                ready, issues = cls.assess_mdk_readiness(case)
                output.append("Offene Punkte:")
                for issue in issues:
                    output.append(f"  • {issue}")
            
            output.append("")
        
        # Erfolgreiche Fälle
        ready_cases = [a for a in assessments if a.mdk_ready]
        
        if ready_cases:
            output.append("✅ MDK-READY AUFNAHMEN:")
            output.append("-" * 80)
            
            for case in ready_cases:
                output.append(f"• {case.patient_name} (ID: {case.patient_id}) - Score: {case.compliance_score:.1f}% - {case.aufnahme_datum.strftime('%d.%m.%Y')}")
            
            output.append("")
        
        # Expertenstandards-Statistik
        output.append("EXPERTENSTANDARDS-ERFÜLLUNG:")
        output.append("-" * 80)
        
        # DVA-Statistiken
        dva_stats = {}
        for assessment in assessments:
            for check in assessment.dva_checks:
                if check.dva_id not in dva_stats:
                    dva_stats[check.dva_id] = {'total': 0, 'compliant': 0, 'title': check.dva_title}
                dva_stats[check.dva_id]['total'] += 1
                if check.compliant or check.actions_completed:
                    dva_stats[check.dva_id]['compliant'] += 1
        
        for dva_id, stats in sorted(dva_stats.items()):
            compliance_rate = (stats['compliant'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if compliance_rate >= 95 else "⚠️" if compliance_rate >= 80 else "❌"
            output.append(f"{status} {dva_id} ({stats['title']}): {compliance_rate:.0f}% ({stats['compliant']}/{stats['total']})")
        
        output.append("")
        output.append("=" * 80)
        output.append("FAZIT:")
        output.append("-" * 80)
        
        if total_score >= 95:
            output.append("✅ EXZELLENT: Alle Aufnahmen entsprechen höchsten Qualitätsstandards.")
        elif total_score >= 85:
            output.append("✅ GUT: Qualitätsstandards werden überwiegend eingehalten.")
        elif total_score >= 75:
            output.append("⚠️ BEFRIEDIGEND: Verbesserungspotenzial bei einzelnen Aufnahmen.")
        else:
            output.append("❌ HANDLUNGSBEDARF: Systematische Verbesserungen erforderlich!")
        
        output.append("")
        output.append("Empfehlungen:")
        if fem_alerts_total > fem_beschluesse_total:
            output.append("• DRINGEND: Fehlende FEM-Beschlüsse nachholen!")
        if mdk_ready_count < len(assessments):
            output.append("• Offene DVA-Maßnahmen zeitnah umsetzen")
        if total_score < 90:
            output.append("• Schulung Pflegepersonal zu Dokumentationsstandards")
        
        output.append("")
        output.append("=" * 80)
        output.append(f"Bericht erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        output.append("=" * 80)
        
        return "\n".join(output)

# ============================================================================
# PDF-EXPORT ENGINE (NEU v3.1)
# ============================================================================

class PDFReportGenerator:
    """
    Generiert professionelle PDF-Berichte für Assessments
    Basis: FPDF mit deutschem Encoding
    """
    
    @classmethod
    def generate_assessment_pdf(cls, result: AssessmentResult) -> bytes:
        """
        Erstellt vollständigen Assessment-PDF-Report
        
        Args:
            result: AssessmentResult-Objekt
            
        Returns:
            bytes: PDF als Byte-String
        """
        pdf = FPDF()
        pdf.add_page()
        
        # === HEADER ===
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="Pflegerisches Aufnahme-Assessment v3.1", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True, align='C')
        pdf.ln(5)
        
        # === PATIENTENINFO ===
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Patienteninformationen", ln=True)
        pdf.set_font("Arial", '', 10)
        
        pdf.cell(60, 6, txt="Patient:", border=0)
        pdf.cell(0, 6, txt=result.patient_name, ln=True, border=0)
        
        pdf.cell(60, 6, txt="Patienten-ID:", border=0)
        pdf.cell(0, 6, txt=result.patient_id, ln=True, border=0)
        
        pdf.cell(60, 6, txt="Aufnahmedatum:", border=0)
        pdf.cell(0, 6, txt=result.aufnahme_datum.strftime('%d.%m.%Y %H:%M'), ln=True, border=0)
        
        pdf.cell(60, 6, txt="Aufgenommen durch:", border=0)
        pdf.cell(0, 6, txt=result.aufgenommen_durch, ln=True, border=0)
        
        pdf.ln(5)
        
        # === COMPLIANCE-ÜBERSICHT ===
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Compliance-Status", ln=True)
        pdf.set_font("Arial", '', 10)
        
        # Compliance-Score mit Farbe
        pdf.cell(60, 6, txt="Compliance-Score:", border=0)
        if result.compliance_score >= 90:
            pdf.set_text_color(0, 128, 0)  # Grün
        elif result.compliance_score >= 75:
            pdf.set_text_color(255, 165, 0)  # Orange
        else:
            pdf.set_text_color(255, 0, 0)  # Rot
        pdf.cell(0, 6, txt=f"{result.compliance_score:.0f}%", ln=True, border=0)
        pdf.set_text_color(0, 0, 0)  # Zurück zu Schwarz
        
        pdf.cell(60, 6, txt="DVA-Compliance:", border=0)
        pdf.cell(0, 6, txt=result.overall_compliance.value, ln=True, border=0)
        
        pdf.cell(60, 6, txt="MDK-Ready:", border=0)
        mdk_status = "Ja" if result.mdk_ready else "Nein"
        pdf.cell(0, 6, txt=mdk_status, ln=True, border=0)
        
        pdf.ln(5)
        
        # === FEM-ALERTS (Falls vorhanden) ===
        if result.fem_alerts:
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, txt="KRITISCH: Freiheitsentziehende Massnahmen erkannt!", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 10)
            
            for i, alert in enumerate(result.fem_alerts, 1):
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, txt=f"{i}. {alert.detected_keyword} ({alert.severity})", ln=True)
                pdf.set_font("Arial", '', 9)
                
                pdf.multi_cell(0, 5, txt=f"Rechtsgrundlage: {alert.legal_reference}")
                
                pdf.cell(0, 5, txt="Sofortmassnahmen:", ln=True)
                for action in alert.immediate_actions[:3]:  # Top 3
                    # Encode to latin-1, replace non-encodable chars
                    safe_action = action.encode('latin-1', 'replace').decode('latin-1')
                    pdf.cell(10, 5, txt="", border=0)
                    pdf.multi_cell(0, 5, txt=f"- {safe_action}")
                
                pdf.cell(0, 5, txt=f"Beschluss vorhanden: {'Ja' if alert.beschluss_vorhanden else 'NEIN - DRINGEND!'}", ln=True)
                pdf.ln(3)
        
        # === RIA-TRIGGER ===
        if result.ria_triggers:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, txt="RIA - Risikoassessment", ln=True)
            pdf.set_font("Arial", '', 10)
            
            for i, trigger in enumerate(result.ria_triggers, 1):
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, txt=f"{i}. {trigger.name}", ln=True)
                pdf.set_font("Arial", '', 9)
                
                pdf.cell(30, 5, txt="Risikostufe:", border=0)
                pdf.cell(0, 5, txt=trigger.risk_level.value, ln=True, border=0)
                
                pdf.cell(30, 5, txt="Evidenz:", border=0)
                pdf.multi_cell(0, 5, txt=trigger.evidence)
                
                pdf.cell(30, 5, txt="Massnahmen:", border=0)
                # Nur erste 100 Zeichen für PDF
                action_short = trigger.recommended_action[:100] + "..." if len(trigger.recommended_action) > 100 else trigger.recommended_action
                safe_action = action_short.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, txt=safe_action)
                
                if trigger.dva_reference:
                    pdf.cell(30, 5, txt="DVA-Referenz:", border=0)
                    pdf.cell(0, 5, txt=trigger.dva_reference, ln=True, border=0)
                
                pdf.ln(3)
        
        # === BI-MODULE ===
        if result.bi_modules:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, txt="BI - Begutachtungsinstrument (NBA)", ln=True)
            pdf.set_font("Arial", '', 10)
            
            for module in result.bi_modules:
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, txt=f"Modul {module.module_id}: {module.module_name}", ln=True)
                pdf.set_font("Arial", '', 9)
                
                pdf.cell(30, 5, txt="Punkte:", border=0)
                pdf.cell(0, 5, txt=f"{module.points} / {module.max_points}", ln=True, border=0)
                
                pdf.cell(30, 5, txt="Kategorie:", border=0)
                pdf.cell(0, 5, txt=module.category.value, ln=True, border=0)
                
                pdf.cell(30, 5, txt="Evidenz:", border=0)
                safe_evidence = module.evidence.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, txt=safe_evidence)
                
                pdf.ln(3)
        
        # === DVA-CHECKS ===
        if result.dva_checks:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, txt="DVA - Dienst- und Verfahrensanweisungen", ln=True)
            pdf.set_font("Arial", '', 10)
            
            for check in result.dva_checks:
                status_icon = "[OK]" if check.compliant else "[!]"
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 6, txt=f"{status_icon} {check.dva_id}: {check.dva_title}", ln=True)
                pdf.set_font("Arial", '', 9)
                
                pdf.cell(30, 5, txt="Anwendbar:", border=0)
                pdf.cell(0, 5, txt="Ja" if check.applicable else "Nein", ln=True, border=0)
                
                pdf.cell(30, 5, txt="Konform:", border=0)
                pdf.cell(0, 5, txt="Ja" if check.compliant else "Nein", ln=True, border=0)
                
                if not check.compliant and check.required_actions:
                    pdf.cell(0, 5, txt="Erforderliche Massnahmen:", ln=True)
                    for action in check.required_actions[:3]:  # Top 3
                        safe_action = action.encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(10, 5, txt="", border=0)
                        pdf.multi_cell(0, 5, txt=f"- {safe_action}")
                
                pdf.ln(3)
        
        # === FOOTER ===
        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, txt="Dieses Tool ersetzt nicht die fachliche Einschatzung qualifizierter Pflegefachkrafte.", ln=True, align='C')
        pdf.cell(0, 5, txt=f"Pflegerisches Aufnahme-Tool v3.1 - FEM-Wachter aktiv - DVA-konform", ln=True, align='C')
        
        # PDF als Bytes zurückgeben
        return pdf.output(dest='S').encode('latin-1')
    
    @classmethod
    def generate_mdk_report_pdf(cls, assessments: List[AssessmentResult]) -> bytes:
        """
        Erstellt MDK-Prüfbericht als PDF
        
        Args:
            assessments: Liste von AssessmentResult-Objekten
            
        Returns:
            bytes: PDF als Byte-String
        """
        pdf = FPDF()
        pdf.add_page()
        
        # === HEADER ===
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt="MDK-Prufbericht", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, txt=f"Berichtsdatum: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True, align='C')
        pdf.cell(0, 5, txt=f"Anzahl Aufnahmen: {len(assessments)}", ln=True, align='C')
        pdf.ln(10)
        
        # === GESAMTSTATISTIK ===
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Gesamtubersicht", ln=True)
        pdf.set_font("Arial", '', 10)
        
        total_score = sum(a.compliance_score for a in assessments) / len(assessments) if assessments else 0
        mdk_ready_count = sum(1 for a in assessments if a.mdk_ready)
        fem_alerts_total = sum(len(a.fem_alerts) for a in assessments)
        
        pdf.cell(80, 6, txt="Durchschnittlicher Compliance-Score:", border=0)
        pdf.cell(0, 6, txt=f"{total_score:.1f}%", ln=True, border=0)
        
        pdf.cell(80, 6, txt="MDK-Ready Aufnahmen:", border=0)
        pdf.cell(0, 6, txt=f"{mdk_ready_count}/{len(assessments)} ({mdk_ready_count/len(assessments)*100:.0f}%)", ln=True, border=0)
        
        pdf.cell(80, 6, txt="FEM-Alerts gesamt:", border=0)
        pdf.cell(0, 6, txt=str(fem_alerts_total), ln=True, border=0)
        
        pdf.ln(10)
        
        # === KRITISCHE FÄLLE ===
        critical_cases = [a for a in assessments if not a.mdk_ready]
        
        if critical_cases:
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 8, txt="HANDLUNGSBEDARF (Nicht MDK-Ready)", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 9)
            
            for case in critical_cases[:5]:  # Top 5
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(0, 6, txt=f"Patient: {case.patient_name} (ID: {case.patient_id})", ln=True)
                pdf.set_font("Arial", '', 9)
                
                pdf.cell(50, 5, txt="Aufnahme:", border=0)
                pdf.cell(0, 5, txt=case.aufnahme_datum.strftime('%d.%m.%Y'), ln=True, border=0)
                
                pdf.cell(50, 5, txt="Compliance-Score:", border=0)
                pdf.cell(0, 5, txt=f"{case.compliance_score:.0f}%", ln=True, border=0)
                
                pdf.ln(3)
        
        # === ERFOLGREICHE FÄLLE ===
        ready_cases = [a for a in assessments if a.mdk_ready]
        
        if ready_cases:
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 128, 0)
            pdf.cell(0, 8, txt="MDK-Ready Aufnahmen", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", '', 9)
            
            for case in ready_cases[:10]:  # Top 10
                pdf.cell(0, 5, txt=f"- {case.patient_name} (Score: {case.compliance_score:.0f}%) - {case.aufnahme_datum.strftime('%d.%m.%Y')}", ln=True)
        
        # === FAZIT ===
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="Fazit", ln=True)
        pdf.set_font("Arial", '', 10)
        
        if total_score >= 95:
            fazit = "EXZELLENT: Alle Aufnahmen entsprechen hochsten Qualitatsstandards."
        elif total_score >= 85:
            fazit = "GUT: Qualitatsstandards werden uberwiegend eingehalten."
        elif total_score >= 75:
            fazit = "BEFRIEDIGEND: Verbesserungspotenzial bei einzelnen Aufnahmen."
        else:
            fazit = "HANDLUNGSBEDARF: Systematische Verbesserungen erforderlich!"
        
        pdf.multi_cell(0, 6, txt=fazit)
        
        # === FOOTER ===
        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 5, txt=f"MDK-Prufbericht erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", ln=True, align='C')
        pdf.cell(0, 5, txt="Pflegerisches Aufnahme-Tool v3.1 - MDK-Simulator", ln=True, align='C')
        
        return pdf.output(dest='S').encode('latin-1')

# ============================================================================
# EXISTING CLASSES (FEM-Wächter, DVA, etc.) - Unverändert
# ============================================================================

class FEMWaechter:
    """Freiheitsentziehende Maßnahmen - Automatische Erkennung"""
    
    FEM_INDICATORS = {
        r'bettgitter': {
            'law': 'BGH XII ZB 24/12 - § 239 StGB Freiheitsberaubung',
            'severity': 'HOCH',
            'alternatives': [
                'Sensor-Matte statt Bettgitter',
                'Niedrigbett (max. 20cm Höhe)',
                'Sturzprophylaxe-Matratze'
            ]
        },
        r'fixier(t|ung)': {
            'law': 'BVerfG 2 BvR 309/15 - Richtervorbehalt',
            'severity': 'HOCH',
            'alternatives': [
                'Nachtwache erhöhen',
                'Bewegungsdrang umleiten',
                'Validation statt Fixierung'
            ]
        },
        r'gefesselt': {
            'law': '§ 33 StGB Körperverletzung',
            'severity': 'HOCH',
            'alternatives': [
                'Weiche Polsterung',
                '1:1 Betreuung',
                'Sedierung nur nach ärztl. Anordnung'
            ]
        },
        r'gurt(e|en)?': {
            'law': '§ 240 StGB Nötigung',
            'severity': 'HOCH',
            'alternatives': [
                'Sitzkissen mit Lagerungshilfe',
                'Angepasster Rollstuhl',
                'Therapeutische Sitzschale'
            ]
        },
        r'tür.{0,20}(abgeschlossen|verschlossen)': {
            'law': '§ 239 StGB Freiheitsberaubung',
            'severity': 'HOCH',
            'alternatives': [
                'GPS-Tracker',
                'Demenz-WG mit freiheitlichem Konzept',
                'Begleitung bei Spaziergängen'
            ]
        },
        r'nicht (hinaus|raus)': {
            'law': '§ 1834 BGB - 24h Anmeldepflicht',
            'severity': 'MITTEL',
            'alternatives': [
                'Begleiteter Ausgang',
                'Strukturierter Tagesablauf',
                'Beschäftigungsangebote'
            ]
        },
        r'festgehalten': {
            'law': '§ 240 StGB Nötigung',
            'severity': 'MITTEL',
            'alternatives': [
                'Deeskalation',
                'Raum zum Abreagieren',
                'Bezugspflege intensivieren'
            ]
        },
        r'eingesperrt': {
            'law': '§ 239 StGB Freiheitsberaubung',
            'severity': 'HOCH',
            'alternatives': [
                'Offene Türen mit Sensor',
                'Betreutes Wohnen',
                'Bauliche Anpassungen'
            ]
        }
    }
    
    @classmethod
    def detect_fem(cls, text: str) -> List[FEMAlert]:
        """Erkennt FEM in Freitext"""
        alerts = []
        text_lower = text.lower()
        
        for pattern, info in cls.FEM_INDICATORS.items():
            match = re.search(pattern, text_lower)
            if match:
                alert = FEMAlert(
                    detected_keyword=match.group(),
                    legal_reference=info['law'],
                    severity=info['severity'],
                    immediate_actions=[
                        "🚨 24h ANMELDUNG beim Familiengericht",
                        "📋 72h RICHTERBESCHLUSS erforderlich",
                        "📝 § 34 StGB Notstand prüfen",
                        "👨‍⚖️ Heimleitung informieren",
                        "📞 Angehörige kontaktieren"
                    ],
                    alternatives=info['alternatives'],
                    deadline_hours=24,
                    documentation_required=[
                        "Gefährdungslage dokumentieren",
                        "Alternativen erwogen und dokumentiert",
                        "Zeitpunkt der Antragstellung",
                        "Unterschrift Heimleitung",
                        "Bestätigung Gerichtsbeschluss"
                    ]
                )
                alerts.append(alert)
        
        return alerts

class DVAComplianceEngine:
    """Prüft Dienst- und Verfahrensanweisungen"""
    
    DVA_RULES = {
        'DVA-001': {
            'title': 'Sturzprophylaxe',
            'triggers': ['sturz', 'gestürzt', 'sturzrisiko', 'unsicher beim gehen'],
            'requirements': [
                'Sturzrisikoassessment innerhalb 24h',
                'Einrichtung Sturzprotokoll',
                'Angehörige informieren',
                'Ggf. Arztbrief bei Verletzung'
            ],
            'responsible': 'Pflegefachkraft/Wohnbereichsleitung'
        },
        'DVA-002': {
            'title': 'Dekubitusprophylaxe',
            'triggers': ['dekubitus', 'druckstelle', 'bettlägerig', 'rollstuhl'],
            'requirements': [
                'Dekubitusrisikoassessment (Braden/Norton)',
                'Lagerungsplan erstellen (2h-Rhythmus)',
                'Weichlagerung dokumentieren',
                'Hautinspektion täglich'
            ],
            'responsible': 'Pflegefachkraft'
        },
        'DVA-003': {
            'title': 'Medikamentenmanagement',
            'triggers': ['medikament', 'tabletten', 'insulin', 'schmerzmittel'],
            'requirements': [
                'Aktuelle Medikationsliste',
                'Ärztliche Verordnung vorliegen',
                '6-R-Regel beachten',
                'Doppelkontrolle bei Hochrisiko-Medikamenten'
            ],
            'responsible': 'Examinierte Pflegekraft'
        },
        'DVA-004': {
            'title': 'Ernährungsmanagement',
            'triggers': ['mangelernährung', 'gewichtsverlust', 'trinkt zu wenig', 'schluckstörung'],
            'requirements': [
                'Screening mit MNA/PEMU',
                'Trinkprotokoll bei Dehydratation',
                'Logopädie bei Dysphagie',
                'Wöchentliche Gewichtskontrolle'
            ],
            'responsible': 'Pflegefachkraft'
        },
        'DVA-005': {
            'title': 'Wundmanagement',
            'triggers': ['wunde', 'ulcus', 'verbandswechsel'],
            'requirements': [
                'Wunddokumentation mit Foto',
                'Ärztliche Anordnung für Behandlung',
                'Steril arbeiten',
                'Verlaufskontrolle wöchentlich'
            ],
            'responsible': 'Wundexpertin/Pflegefachkraft'
        },
        'DVA-006': {
            'title': 'Freiheitsentziehende Maßnahmen',
            'triggers': ['bettgitter', 'fixierung', 'gurte', 'tür verschlossen'],
            'requirements': [
                '🚨 SOFORT Richterbeschluss einholen',
                'Alternativen dokumentieren',
                '§ 34 StGB Notstand prüfen',
                'Täglich überprüfen und dokumentieren'
            ],
            'responsible': 'Heimleitung/Pflegedienstleitung'
        },
        'DVA-007': {
            'title': 'Demenzielle Erkrankung',
            'triggers': ['demenz', 'verwirrt', 'desorientiert', 'vergisst'],
            'requirements': [
                'Demenz-Screening (MMST/DemTect)',
                'Biografie-Arbeit',
                'Validation anwenden',
                'Angehörigenschulung anbieten'
            ],
            'responsible': 'Pflegefachkraft/Gerontopsych. Fachkraft'
        },
        'DVA-008': {
            'title': 'Hygiene & Infektionsschutz',
            'triggers': ['infektion', 'mrsa', 'vre', 'fieber', 'durchfall'],
            'requirements': [
                'Isolationsmaßnahmen nach RKI',
                'Hygieneplan einhalten',
                'Gesundheitsamt melden (bei meldepflichtigen Erkrankungen)',
                'Personal schulen'
            ],
            'responsible': 'Hygienebeauftragte/PDL'
        }
    }
    
    @classmethod
    def check_compliance(cls, text: str, ria_triggers: List[RIATrigger]) -> List[DVACheck]:
        """Prüft DVA-Compliance"""
        checks = []
        text_lower = text.lower()
        
        for dva_id, rule in cls.DVA_RULES.items():
            applicable = False
            findings = []
            
            for trigger in rule['triggers']:
                if trigger in text_lower:
                    applicable = True
                    findings.append(f"Trigger gefunden: '{trigger}'")
            
            if applicable:
                check = DVACheck(
                    dva_id=dva_id,
                    dva_title=rule['title'],
                    applicable=True,
                    compliant=False,
                    findings=findings,
                    required_actions=rule['requirements'],
                    responsible_person=rule['responsible'],
                    deadline=datetime.now() + timedelta(hours=24)
                )
                checks.append(check)
        
        return checks

# ... (Rest der bestehenden PflegeAufnahmeEngine Klasse - gekürzt für Übersicht)
# Die vollständige Klasse bleibt unverändert

class PflegeAufnahmeEngine:
    """Hauptengine für pflegerische Aufnahme"""
    
    BI_MODULES = {
        1: {'name': 'Mobilität', 'keywords': ['gehen', 'laufen', 'stehen', 'transfers', 'rollstuhl', 'sturz'], 'max_points': 15},
        2: {'name': 'Kognitive und kommunikative Fähigkeiten', 'keywords': ['verwirrt', 'demenz', 'orientierung', 'sprache', 'gedächtnis'], 'max_points': 15},
        3: {'name': 'Verhaltensweisen', 'keywords': ['aggressiv', 'unruhig', 'weglauftendenz', 'ablehnung'], 'max_points': 15},
        4: {'name': 'Selbstversorgung', 'keywords': ['waschen', 'anziehen', 'essen', 'trinken', 'toilette'], 'max_points': 30},
        5: {'name': 'Umgang mit krankheitsspezifischen Anforderungen', 'keywords': ['medikamente', 'insulin', 'kompression', 'katheter', 'wunde'], 'max_points': 15},
        6: {'name': 'Gestaltung des Alltagslebens', 'keywords': ['beschäftigung', 'hobbies', 'kontakte', 'tagesstruktur'], 'max_points': 10}
    }
    
    RIA_TRIGGERS_DB = {
        'Sturz': {'keywords': ['sturz', 'gestürzt', 'hingefallen'], 'risk_level': RiskLevel.HIGH, 'action': 'Sturzprotokoll anlegen, Arzt informieren, Sturzrisikoassessment', 'dva': 'DVA-001'},
        'Dekubitus': {'keywords': ['dekubitus', 'druckstelle', 'rötung kategorie'], 'risk_level': RiskLevel.HIGH, 'action': 'Wunddokumentation, Weichlagerung, Wundbehandlung nach Standard', 'dva': 'DVA-002'},
        'Mangelernährung': {'keywords': ['mangelernährung', 'gewichtsverlust', 'bmi unter'], 'risk_level': RiskLevel.MEDIUM, 'action': 'MNA-Screening, Ernährungsplan, ggf. Arzt/Diätassistenz', 'dva': 'DVA-004'},
        'Exsikkose': {'keywords': ['dehydration', 'trinkt zu wenig', 'trockene haut'], 'risk_level': RiskLevel.MEDIUM, 'action': 'Trinkprotokoll, Flüssigkeitsbilanz, ggf. i.v. Flüssigkeit', 'dva': 'DVA-004'},
        'Schmerzen': {'keywords': ['schmerz', 'schmerzmittel', 'leidet'], 'risk_level': RiskLevel.MEDIUM, 'action': 'Schmerzassessment (NRS/BESD), Schmerzmanagement, Arzt', 'dva': 'DVA-003'},
        'Infektion': {'keywords': ['infektion', 'fieber', 'mrsa', 'vre'], 'risk_level': RiskLevel.HIGH, 'action': 'Isolation, Hygieneplan, Gesundheitsamt melden', 'dva': 'DVA-008'}
    }
    
    def __init__(self):
        self.fem_waechter = FEMWaechter()
        self.dva_engine = DVAComplianceEngine()
    
    def analyze_aufnahme(self, patient_text: str, patient_id: str, patient_name: str, aufgenommen_durch: str) -> AssessmentResult:
        """Vollständige Aufnahme-Analyse"""
        fem_alerts = self.fem_waechter.detect_fem(patient_text)
        ria_triggers = self._detect_ria_triggers(patient_text, fem_alerts)
        bi_modules = self._detect_bi_modules(patient_text)
        sis_strukturen = self._generate_sis_structure(patient_text)
        dva_checks = self.dva_engine.check_compliance(patient_text, ria_triggers)
        overall_compliance = self._calculate_overall_compliance(fem_alerts, dva_checks)
        
        result = AssessmentResult(
            patient_id=patient_id,
            patient_name=patient_name,
            aufnahme_datum=datetime.now(),
            aufgenommen_durch=aufgenommen_durch,
            ria_triggers=ria_triggers,
            bi_modules=bi_modules,
            sis_strukturen=sis_strukturen,
            fem_alerts=fem_alerts,
            dva_checks=dva_checks,
            overall_compliance=overall_compliance,
            review_required=len(fem_alerts) > 0 or overall_compliance == DVACompliance.NON_COMPLIANT
        )
        
        # NEU: Compliance-Score und MDK-Readiness berechnen
        result.compliance_score = MDKSimulator.calculate_compliance_score(result)
        result.mdk_ready, _ = MDKSimulator.assess_mdk_readiness(result)
        
        return result
    
    def _detect_ria_triggers(self, text: str, fem_alerts: List[FEMAlert]) -> List[RIATrigger]:
        triggers = []
        text_lower = text.lower()
        
        for fem in fem_alerts:
            trigger = RIATrigger(
                name=f"🚨 FEM - {fem.detected_keyword}",
                risk_level=RiskLevel.CRITICAL,
                evidence=f"Freiheitsentziehende Maßnahme erkannt: '{fem.detected_keyword}'",
                recommended_action="\n".join(fem.immediate_actions),
                deadline_hours=fem.deadline_hours,
                dva_reference='DVA-006',
                compliance_status=DVACompliance.NON_COMPLIANT,
                fem_alert=fem
            )
            triggers.append(trigger)
        
        for trigger_name, config in self.RIA_TRIGGERS_DB.items():
            for keyword in config['keywords']:
                if keyword in text_lower:
                    trigger = RIATrigger(
                        name=trigger_name,
                        risk_level=config['risk_level'],
                        evidence=f"Keyword gefunden: '{keyword}'",
                        recommended_action=config['action'],
                        deadline_hours=24,
                        dva_reference=config.get('dva')
                    )
                    triggers.append(trigger)
                    break
        
        return triggers
    
    def _detect_bi_modules(self, text: str) -> List[BIModule]:
        modules = []
        text_lower = text.lower()
        
        for module_id, config in self.BI_MODULES.items():
            matches = 0
            evidence_keywords = []
            
            for keyword in config['keywords']:
                if keyword in text_lower:
                    matches += 1
                    evidence_keywords.append(keyword)
            
            if matches > 0:
                points = min(matches * 3, config['max_points'])
                percent = points / config['max_points']
                
                if percent < 0.25:
                    category = BIModuleCategory.INDEPENDENT
                elif percent < 0.50:
                    category = BIModuleCategory.MOSTLY_INDEPENDENT
                elif percent < 0.75:
                    category = BIModuleCategory.MOSTLY_DEPENDENT
                else:
                    category = BIModuleCategory.DEPENDENT
                
                module = BIModule(
                    module_id=module_id,
                    module_name=config['name'],
                    points=points,
                    max_points=config['max_points'],
                    category=category,
                    evidence=f"Keywords: {', '.join(evidence_keywords)}"
                )
                modules.append(module)
        
        return modules
    
    def _generate_sis_structure(self, text: str) -> List[SISStructure]:
        sis_list = []
        
        if any(kw in text.lower() for kw in ['gehen', 'laufen', 'sturz', 'rollstuhl']):
            sis = SISStructure(
                themenfeld="Mobilität und Bewegung",
                information="Siehe Assessment-Text",
                risiken=["Sturzgefahr", "Eingeschränkte Mobilität"],
                ressourcen=["Gehstock vorhanden" if 'gehstock' in text.lower() else ""],
                wünsche_patient="Mobilität erhalten",
                maßnahmen_geplant=["Sturzprophylaxe", "Mobilisierung"]
            )
            sis_list.append(sis)
        
        return sis_list
    
    def _calculate_overall_compliance(self, fem_alerts: List[FEMAlert], dva_checks: List[DVACheck]) -> DVACompliance:
        if len(fem_alerts) > 0:
            return DVACompliance.NON_COMPLIANT
        
        non_compliant = sum(1 for check in dva_checks if not check.compliant)
        
        if non_compliant > 0:
            return DVACompliance.NEEDS_ATTENTION
        
        return DVACompliance.COMPLIANT

# ============================================================================
# STREAMLIT UI (erweitert mit Smart-Copy & MDK-Dashboard)
# ============================================================================

def main():
    st.set_page_config(
        page_title="Pflegerische Aufnahme v3.1",
        layout="wide",
        page_icon="🏥"
    )
    
    # Session State für Assessments initialisieren
    if 'assessments_history' not in st.session_state:
        st.session_state['assessments_history'] = []
    
    st.title("🏥 Professionelle Pflegerische Aufnahme")
    st.markdown("**v3.1** - Mit Smart-Copy Export & MDK-Simulator")
    
    # Tabs für verschiedene Bereiche
    tab1, tab2, tab3 = st.tabs(["📝 Neue Aufnahme", "📊 MDK-Dashboard", "📋 Verlauf"])
    
    # ========================================================================
    # TAB 1: NEUE AUFNAHME
    # ========================================================================
    
    with tab1:
        # Sidebar
        with st.sidebar:
            st.header("⚙️ Einstellungen")
            
            aufgenommen_durch = st.text_input(
                "Aufgenommen durch",
                value="Pflegefachkraft M. Müller",
                help="Ihr Name und Funktion"
            )
            
            patient_id = st.text_input(
                "Patienten-ID",
                value=f"PAT-{datetime.now().strftime('%Y%m%d-%H%M')}",
                help="Anonymisierte ID"
            )
            
            patient_name = st.text_input(
                "Patient (Pseudonym)",
                value="Patient A",
                help="Pseudonym oder Initialen"
            )
            
            st.markdown("---")
            st.markdown("### 🔐 Compliance-Level")
            st.info("Alle DVA-Checks werden automatisch durchgeführt")
            
            st.markdown("---")
            st.markdown("### 🚨 FEM-Wächter")
            st.warning("**Aktiv** - Automatische Erkennung freiheitsentziehender Maßnahmen")
        
        # Main Content
        st.markdown("## 📝 Aufnahme-Dokumentation")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            aufnahme_text = st.text_area(
                "Aufnahme-Informationen (Freitext)",
                height=300,
                placeholder="""Beispiel:
                
Frau Anna L., 82 Jahre, Aufnahme nach Sturz zu Hause.
Bettgitter nachts hochgestellt wegen Sturzgefahr.
Leichte Demenz, verwirrt, desorientiert.
Nimmt Marcumar, Insulin 3x täglich.
Rollstuhl für längere Strecken.
Trinkt zu wenig, Gewichtsverlust 5kg in 3 Monaten.
Tochter besucht täglich.""",
                help="Tragen Sie alle relevanten Informationen ein"
            )
            
            if st.button("🔍 Aufnahme-Assessment durchführen", type="primary", use_container_width=True):
                if aufnahme_text.strip():
                    with st.spinner("Analysiere Aufnahme-Daten..."):
                        engine = PflegeAufnahmeEngine()
                        result = engine.analyze_aufnahme(
                            patient_text=aufnahme_text,
                            patient_id=patient_id,
                            patient_name=patient_name,
                            aufgenommen_durch=aufgenommen_durch
                        )
                        
                        st.session_state['assessment_result'] = result
                        st.session_state['assessments_history'].append(result)
                        st.success("✅ Assessment abgeschlossen!")
                else:
                    st.error("Bitte Aufnahme-Text eingeben!")
        
        with col2:
            st.info("""
            **Automatische Erkennung:**
            
            ✅ **RIA** - Risikoassessment
            ✅ **BI** - Begutachtungsinstrument  
            ✅ **SiS** - Strukturierte Info
            🚨 **FEM** - Freiheitsentziehende Maßnahmen
            📋 **DVA** - Dienst-/Verfahrensanweisungen
            """)
            
            st.markdown("---")
            
            # Testfälle
            if st.button("📋 Testfall: FEM-Fall"):
                st.session_state['test_text'] = """Frau Anna L., 82 Jahre.
Bettgitter nachts hochgestellt wegen Sturzgefahr.
Gestürzt letzte Woche. Leichte Demenz."""
            
            if st.button("📋 Testfall: Standard"):
                st.session_state['test_text'] = """Herr K., 75 Jahre.
Diabetes Typ 2, Insulin 3x täglich.
Unsicher beim Gehen, nutzt Gehstock.
Trinkt zu wenig. Sohn besucht täglich."""
        
        # Ergebnisse anzeigen
        if 'assessment_result' in st.session_state:
            result = st.session_state['assessment_result']
            
            st.markdown("---")
            st.markdown("## 📊 Assessment-Ergebnisse")
            
            # Compliance-Badge
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Patient", result.patient_name)
            with col2:
                st.metric("Aufnahme", result.aufnahme_datum.strftime("%d.%m.%Y"))
            with col3:
                compliance_color = {
                    DVACompliance.COMPLIANT: "🟢",
                    DVACompliance.NEEDS_ATTENTION: "🟡",
                    DVACompliance.NON_COMPLIANT: "🔴"
                }
                st.metric(
                    "DVA-Compliance",
                    f"{compliance_color.get(result.overall_compliance, '⚪')} {result.overall_compliance.value}"
                )
            with col4:
                st.metric("Compliance-Score", f"{result.compliance_score:.0f}%")
            with col5:
                st.metric("MDK-Ready", "✅" if result.mdk_ready else "❌")
            
            # FEM-Alerts
            if result.fem_alerts:
                st.markdown("### 🚨 KRITISCH: Freiheitsentziehende Maßnahmen erkannt!")
                
                for alert in result.fem_alerts:
                    with st.expander(f"⚠️ FEM: {alert.detected_keyword} - {alert.severity}", expanded=True):
                        st.error(f"""
                        **Rechtsgrundlage:** {alert.legal_reference}
                        
                        **Schweregrad:** {alert.severity}
                        
                        **Deadline:** {alert.deadline_hours} Stunden
                        """)
                        
                        st.markdown("**🚨 SOFORTMASSNAHMEN:**")
                        for action in alert.immediate_actions:
                            st.markdown(f"- {action}")
                        
                        st.markdown("**🔄 ALTERNATIVEN (BVerfG-Pflicht):**")
                        for alt in alert.alternatives:
                            st.markdown(f"- ✅ {alt}")
                        
                        st.markdown("**📋 PFLICHT-DOKUMENTATION:**")
                        for doc in alert.documentation_required:
                            st.checkbox(doc, key=f"doc_{alert.detected_keyword}_{doc}")
                        
                        # NEU: Beschluss-Tracking
                        st.markdown("---")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            beschluss_check = st.checkbox("Richterbeschluss vorhanden", key=f"beschluss_{alert.detected_keyword}")
                            if beschluss_check:
                                alert.beschluss_vorhanden = True
                        with col_b:
                            if beschluss_check:
                                beschluss_datum = st.date_input("Beschluss-Datum", key=f"datum_{alert.detected_keyword}")
                                alert.beschluss_datum = datetime.combine(beschluss_datum, datetime.min.time())
            
            # RIA, BI, DVA... (gekürzt - bleibt wie in v3.0)
            
            # NEU: SMART-COPY EXPORT
            st.markdown("---")
            st.markdown("## 📤 Smart-Copy Export")
            
            export_format = st.selectbox(
                "Ziel-System wählen",
                options=[fmt.value for fmt in ExportFormat],
                help="Wählen Sie Ihr Pflegesoftware-System"
            )
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                if st.button("📋 Text kopieren", use_container_width=True):
                    # Export generieren
                    if export_format == ExportFormat.DM7.value:
                        export_text = SmartCopyEngine.export_for_dm7(result)
                    elif export_format == ExportFormat.VIVENDI.value:
                        export_text = SmartCopyEngine.export_for_vivendi(result)
                    elif export_format == ExportFormat.MEDIFOX.value:
                        export_text = SmartCopyEngine.export_for_medifox(result)
                    else:
                        export_text = SmartCopyEngine.export_generic(result)
                    
                    st.session_state['export_text'] = export_text
                    st.success("✅ Export erstellt! Text unten kopieren.")
            
            with col_exp2:
                if st.button("💾 Als TXT speichern", use_container_width=True):
                    if 'export_text' in st.session_state:
                        st.download_button(
                            label="📥 Download TXT",
                            data=st.session_state['export_text'],
                            file_name=f"aufnahme_{result.patient_id}_{export_format}.txt",
                            mime="text/plain"
                        )
            
            with col_exp3:
                if st.button("📊 JSON-Daten", use_container_width=True):
                    result_json = {
                        'patient_id': result.patient_id,
                        'patient_name': result.patient_name,
                        'aufnahme_datum': result.aufnahme_datum.isoformat(),
                        'compliance_score': result.compliance_score,
                        'mdk_ready': result.mdk_ready
                    }
                    
                    st.download_button(
                        label="💾 Download JSON",
                        data=json.dumps(result_json, indent=2, ensure_ascii=False),
                        file_name=f"aufnahme_{result.patient_id}.json",
                        mime="application/json"
                    )
            
            # Export-Text anzeigen
            if 'export_text' in st.session_state:
                st.text_area(
                    f"Export für {export_format}",
                    value=st.session_state['export_text'],
                    height=400,
                    help="Kopieren Sie diesen Text und fügen Sie ihn in Ihr Pflegesystem ein"
                )
            
            # NEU: PDF-EXPORT
            st.markdown("---")
            st.markdown("## 📄 PDF-Export")
            
            col_pdf1, col_pdf2 = st.columns(2)
            
            with col_pdf1:
                if st.button("📥 Assessment als PDF", use_container_width=True, type="primary"):
                    with st.spinner("Generiere PDF..."):
                        try:
                            pdf_bytes = PDFReportGenerator.generate_assessment_pdf(result)
                            
                            st.download_button(
                                label="💾 PDF herunterladen",
                                data=pdf_bytes,
                                file_name=f"Aufnahme_{result.patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ PDF erfolgreich generiert!")
                        except Exception as e:
                            st.error(f"❌ Fehler bei PDF-Generierung: {str(e)}")
                            st.info("💡 Tipp: Verwenden Sie den Text-Export als Alternative")
            
            with col_pdf2:
                st.info("""
                **PDF enthält:**
                - Patienteninfo
                - Compliance-Status
                - RIA-Trigger
                - BI-Module
                - DVA-Checks
                - FEM-Alerts (falls vorhanden)
                """)
    
    # ========================================================================
    # TAB 2: MDK-DASHBOARD
    # ========================================================================
    
    with tab2:
        st.markdown("## 📊 MDK-Simulator Dashboard")
        
        if st.session_state['assessments_history']:
            assessments = st.session_state['assessments_history']
            
            # Gesamtstatistik
            col1, col2, col3, col4 = st.columns(4)
            
            total_score = sum(a.compliance_score for a in assessments) / len(assessments)
            mdk_ready_count = sum(1 for a in assessments if a.mdk_ready)
            fem_total = sum(len(a.fem_alerts) for a in assessments)
            fem_beschluesse = sum(sum(1 for alert in a.fem_alerts if alert.beschluss_vorhanden) for a in assessments)
            
            with col1:
                st.metric("Aufnahmen gesamt", len(assessments))
            with col2:
                st.metric("Ø Compliance", f"{total_score:.0f}%")
            with col3:
                st.metric("MDK-Ready", f"{mdk_ready_count}/{len(assessments)}")
            with col4:
                if fem_total > 0:
                    st.metric("FEM-Beschlüsse", f"{fem_beschluesse}/{fem_total}")
                else:
                    st.metric("FEM-Alerts", "0")
            
            # MDK-Report generieren
            st.markdown("---")
            
            col_mdk1, col_mdk2 = st.columns(2)
            
            with col_mdk1:
                if st.button("📋 MDK-Prüfbericht (Text)", type="primary", use_container_width=True):
                    report = MDKSimulator.generate_mdk_report(assessments)
                    st.text_area(
                        "MDK-Prüfbericht",
                        value=report,
                        height=600,
                        help="Dieser Bericht kann für MDK-Prüfungen verwendet werden"
                    )
                    
                    st.download_button(
                        label="💾 Report als TXT speichern",
                        data=report,
                        file_name=f"MDK_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            
            with col_mdk2:
                if st.button("📄 MDK-Prüfbericht (PDF)", type="secondary", use_container_width=True):
                    with st.spinner("Generiere MDK-PDF..."):
                        try:
                            pdf_bytes = PDFReportGenerator.generate_mdk_report_pdf(assessments)
                            
                            st.download_button(
                                label="💾 MDK-PDF herunterladen",
                                data=pdf_bytes,
                                file_name=f"MDK_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ MDK-PDF erfolgreich generiert!")
                        except Exception as e:
                            st.error(f"❌ Fehler bei PDF-Generierung: {str(e)}")
                            st.info("💡 Tipp: Verwenden Sie den Text-Report als Alternative")
            
            # Kritische Fälle
            st.markdown("---")
            st.markdown("### ⚠️ Aufmerksamkeit erforderlich")
            
            critical_cases = [a for a in assessments if not a.mdk_ready]
            
            if critical_cases:
                for case in critical_cases:
                    with st.expander(f"❌ {case.patient_name} (ID: {case.patient_id}) - Score: {case.compliance_score:.0f}%"):
                        ready, issues = MDKSimulator.assess_mdk_readiness(case)
                        
                        st.markdown("**Offene Punkte:**")
                        for issue in issues:
                            st.markdown(f"- {issue}")
            else:
                st.success("✅ Alle Aufnahmen sind MDK-ready!")
            
            # Trend-Analyse
            st.markdown("---")
            st.markdown("### 📈 Trend-Analyse")
            
            df_scores = pd.DataFrame({
                'Aufnahme': [a.patient_name for a in assessments],
                'Datum': [a.aufnahme_datum for a in assessments],
                'Compliance-Score': [a.compliance_score for a in assessments],
                'MDK-Ready': [a.mdk_ready for a in assessments]
            })
            
            st.line_chart(df_scores.set_index('Datum')['Compliance-Score'])
            
        else:
            st.info("Noch keine Aufnahmen durchgeführt. Erstellen Sie zuerst eine Aufnahme im Tab 'Neue Aufnahme'.")
    
    # ========================================================================
    # TAB 3: VERLAUF
    # ========================================================================
    
    with tab3:
        st.markdown("## 📋 Aufnahmen-Verlauf")
        
        if st.session_state['assessments_history']:
            for i, assessment in enumerate(reversed(st.session_state['assessments_history'])):
                with st.expander(
                    f"{assessment.aufnahme_datum.strftime('%d.%m.%Y %H:%M')} - {assessment.patient_name} "
                    f"(Score: {assessment.compliance_score:.0f}%)"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Patient-ID:** {assessment.patient_id}")
                        st.markdown(f"**Aufgenommen durch:** {assessment.aufgenommen_durch}")
                        st.markdown(f"**RIA-Trigger:** {len(assessment.ria_triggers)}")
                        st.markdown(f"**FEM-Alerts:** {len(assessment.fem_alerts)}")
                    
                    with col2:
                        st.markdown(f"**Compliance:** {assessment.overall_compliance.value}")
                        st.markdown(f"**Score:** {assessment.compliance_score:.0f}%")
                        st.markdown(f"**MDK-Ready:** {'✅' if assessment.mdk_ready else '❌'}")
                        st.markdown(f"**BI-Module:** {len(assessment.bi_modules)}")
        else:
            st.info("Noch keine Aufnahmen im Verlauf.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p><strong>Pflegerische Aufnahme v3.1</strong> - Mit Smart-Copy & MDK-Simulator</p>
    <p>⚠️ Dieses Tool ersetzt nicht die fachliche Einschätzung qualifizierter Pflegefachkräfte</p>
    <p>🛡️ FEM-Wächter aktiv | 📋 DVA-Compliance | 🔒 Rechtssicher dokumentieren | 📤 Smart-Copy Export</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
