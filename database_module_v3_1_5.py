# Erweiterungen für v3.1.5 Market-Ready
# Teil 2: SQLite-Datenbank für Daten-Persistenz

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import shutil
from pathlib import Path

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """
    SQLite-Datenbank für lokale Persistenz
    
    Features:
    - Automatisches Backup (täglich)
    - Vollständige CRUD-Operationen
    - Export/Import
    - Audit-Trail
    """
    
    def __init__(self, db_path: str = "pflege_tool.db"):
        """
        Initialisiert Datenbank
        
        Args:
            db_path: Pfad zur Datenbank-Datei
        """
        self.db_path = db_path
        self.backup_dir = "backups"
        self._init_database()
        self._init_backup_dir()
    
    def _init_database(self):
        """Erstellt Datenbank-Schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabelle: Assessments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            aufnahme_datum TIMESTAMP NOT NULL,
            aufgenommen_durch TEXT NOT NULL,
            
            -- Spezialisierung (v3.2 vorbereitet)
            specialization TEXT DEFAULT 'GENERAL',
            patient_age_group TEXT,
            
            -- Compliance & MDK
            overall_compliance TEXT NOT NULL,
            compliance_score REAL DEFAULT 0.0,
            mdk_ready INTEGER DEFAULT 0,
            
            -- Review
            review_required INTEGER DEFAULT 0,
            reviewer_name TEXT,
            review_date TIMESTAMP,
            
            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(patient_id, aufnahme_datum)
        )
        """)
        
        # Tabelle: RIA-Trigger
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ria_triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            evidence TEXT,
            recommended_action TEXT,
            deadline_hours INTEGER DEFAULT 24,
            dva_reference TEXT,
            compliance_status TEXT,
            massnahmen_umgesetzt INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        )
        """)
        
        # Tabelle: BI-Module
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bi_modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            module_id INTEGER NOT NULL,
            module_name TEXT NOT NULL,
            points INTEGER NOT NULL,
            max_points INTEGER NOT NULL,
            category TEXT NOT NULL,
            evidence TEXT,
            dva_compliant INTEGER DEFAULT 1,
            compliance_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        )
        """)
        
        # Tabelle: FEM-Alerts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fem_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            detected_keyword TEXT NOT NULL,
            legal_reference TEXT NOT NULL,
            severity TEXT NOT NULL,
            immediate_actions TEXT,  -- JSON
            alternatives TEXT,  -- JSON
            deadline_hours INTEGER NOT NULL,
            documentation_required TEXT,  -- JSON
            beschluss_vorhanden INTEGER DEFAULT 0,
            beschluss_datum TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        )
        """)
        
        # Tabelle: DVA-Checks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dva_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            dva_id TEXT NOT NULL,
            dva_title TEXT NOT NULL,
            applicable INTEGER DEFAULT 1,
            compliant INTEGER DEFAULT 1,
            findings TEXT,  -- JSON
            required_actions TEXT,  -- JSON
            responsible_person TEXT,
            deadline TIMESTAMP,
            actions_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        )
        """)
        
        # Tabelle: SiS-Strukturen
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sis_strukturen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            themenfeld TEXT NOT NULL,
            information TEXT,
            risiken TEXT,  -- JSON
            ressourcen TEXT,  -- JSON
            wuensche_patient TEXT,
            massnahmen_geplant TEXT,  -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        )
        """)
        
        # Tabelle: Audit-Trail
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_trail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER,
            old_value TEXT,  -- JSON
            new_value TEXT,  -- JSON
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabelle: Benutzer (einfaches Login)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,  -- 'admin', 'pdl', 'pflegekraft'
            full_name TEXT,
            email TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """)
        
        # Indices für Performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_id ON assessments(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aufnahme_datum ON assessments(aufnahme_datum)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdk_ready ON assessments(mdk_ready)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessment_id ON ria_triggers(assessment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fem_assessment ON fem_alerts(assessment_id)")
        
        conn.commit()
        conn.close()
    
    def _init_backup_dir(self):
        """Erstellt Backup-Verzeichnis"""
        Path(self.backup_dir).mkdir(exist_ok=True)
    
    # ========================================================================
    # CRUD-OPERATIONEN
    # ========================================================================
    
    def save_assessment(self, assessment: 'AssessmentResult', user: str = 'system') -> int:
        """
        Speichert Assessment in Datenbank
        
        Args:
            assessment: AssessmentResult-Objekt
            user: Benutzername (für Audit-Trail)
            
        Returns:
            assessment_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Assessment-Hauptdaten
            cursor.execute("""
            INSERT INTO assessments (
                patient_id, patient_name, aufnahme_datum, aufgenommen_durch,
                specialization, patient_age_group,
                overall_compliance, compliance_score, mdk_ready,
                review_required, reviewer_name, review_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment.patient_id,
                assessment.patient_name,
                assessment.aufnahme_datum,
                assessment.aufgenommen_durch,
                assessment.specialization.value if hasattr(assessment, 'specialization') else 'GENERAL',
                assessment.patient_age.value if hasattr(assessment, 'patient_age') and assessment.patient_age else None,
                assessment.overall_compliance.value,
                assessment.compliance_score,
                1 if assessment.mdk_ready else 0,
                1 if assessment.review_required else 0,
                assessment.reviewer_name,
                assessment.review_date
            ))
            
            assessment_id = cursor.lastrowid
            
            # RIA-Trigger
            for trigger in assessment.ria_triggers:
                cursor.execute("""
                INSERT INTO ria_triggers (
                    assessment_id, name, risk_level, evidence, recommended_action,
                    deadline_hours, dva_reference, compliance_status, massnahmen_umgesetzt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id,
                    trigger.name,
                    trigger.risk_level.value,
                    trigger.evidence,
                    trigger.recommended_action,
                    trigger.deadline_hours,
                    trigger.dva_reference,
                    trigger.compliance_status.value,
                    1 if trigger.massnahmen_umgesetzt else 0
                ))
            
            # BI-Module
            for module in assessment.bi_modules:
                cursor.execute("""
                INSERT INTO bi_modules (
                    assessment_id, module_id, module_name, points, max_points,
                    category, evidence, dva_compliant, compliance_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id,
                    module.module_id,
                    module.module_name,
                    module.points,
                    module.max_points,
                    module.category.value,
                    module.evidence,
                    1 if module.dva_compliant else 0,
                    module.compliance_notes
                ))
            
            # FEM-Alerts
            for alert in assessment.fem_alerts:
                cursor.execute("""
                INSERT INTO fem_alerts (
                    assessment_id, detected_keyword, legal_reference, severity,
                    immediate_actions, alternatives, deadline_hours, documentation_required,
                    beschluss_vorhanden, beschluss_datum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id,
                    alert.detected_keyword,
                    alert.legal_reference,
                    alert.severity,
                    json.dumps(alert.immediate_actions),
                    json.dumps(alert.alternatives),
                    alert.deadline_hours,
                    json.dumps(alert.documentation_required),
                    1 if alert.beschluss_vorhanden else 0,
                    alert.beschluss_datum
                ))
            
            # DVA-Checks
            for check in assessment.dva_checks:
                cursor.execute("""
                INSERT INTO dva_checks (
                    assessment_id, dva_id, dva_title, applicable, compliant,
                    findings, required_actions, responsible_person, deadline, actions_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id,
                    check.dva_id,
                    check.dva_title,
                    1 if check.applicable else 0,
                    1 if check.compliant else 0,
                    json.dumps(check.findings),
                    json.dumps(check.required_actions),
                    check.responsible_person,
                    check.deadline,
                    1 if check.actions_completed else 0
                ))
            
            # SiS-Strukturen
            for sis in assessment.sis_strukturen:
                cursor.execute("""
                INSERT INTO sis_strukturen (
                    assessment_id, themenfeld, information, risiken, ressourcen,
                    wuensche_patient, massnahmen_geplant
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id,
                    sis.themenfeld,
                    sis.information,
                    json.dumps(sis.risiken),
                    json.dumps(sis.ressourcen),
                    sis.wünsche_patient,
                    json.dumps(sis.maßnahmen_geplant)
                ))
            
            # Audit-Trail
            cursor.execute("""
            INSERT INTO audit_trail (user, action, table_name, record_id, new_value)
            VALUES (?, 'CREATE', 'assessments', ?, ?)
            """, (user, assessment_id, json.dumps({'patient_id': assessment.patient_id})))
            
            conn.commit()
            return assessment_id
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise ValueError(f"Assessment existiert bereits: {e}")
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Fehler beim Speichern: {e}")
        finally:
            conn.close()
    
    def get_assessment(self, assessment_id: int) -> Optional[Dict]:
        """Lädt Assessment aus Datenbank"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
        assessment_row = cursor.fetchone()
        
        if not assessment_row:
            conn.close()
            return None
        
        # RIA-Trigger laden
        cursor.execute("SELECT * FROM ria_triggers WHERE assessment_id = ?", (assessment_id,))
        ria_triggers = [dict(row) for row in cursor.fetchall()]
        
        # BI-Module laden
        cursor.execute("SELECT * FROM bi_modules WHERE assessment_id = ?", (assessment_id,))
        bi_modules = [dict(row) for row in cursor.fetchall()]
        
        # FEM-Alerts laden
        cursor.execute("SELECT * FROM fem_alerts WHERE assessment_id = ?", (assessment_id,))
        fem_alerts = [dict(row) for row in cursor.fetchall()]
        
        # DVA-Checks laden
        cursor.execute("SELECT * FROM dva_checks WHERE assessment_id = ?", (assessment_id,))
        dva_checks = [dict(row) for row in cursor.fetchall()]
        
        # SiS laden
        cursor.execute("SELECT * FROM sis_strukturen WHERE assessment_id = ?", (assessment_id,))
        sis_strukturen = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'assessment': dict(assessment_row),
            'ria_triggers': ria_triggers,
            'bi_modules': bi_modules,
            'fem_alerts': fem_alerts,
            'dva_checks': dva_checks,
            'sis_strukturen': sis_strukturen
        }
    
    def get_all_assessments(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Lädt alle Assessments (paginiert)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM assessments 
        ORDER BY aufnahme_datum DESC 
        LIMIT ? OFFSET ?
        """, (limit, offset))
        
        assessments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return assessments
    
    def delete_assessment(self, assessment_id: int, user: str = 'system'):
        """Löscht Assessment (CASCADE)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Audit-Trail
        cursor.execute("""
        INSERT INTO audit_trail (user, action, table_name, record_id)
        VALUES (?, 'DELETE', 'assessments', ?)
        """, (user, assessment_id))
        
        cursor.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
        
        conn.commit()
        conn.close()
    
    # ========================================================================
    # BACKUP & RESTORE
    # ========================================================================
    
    def create_backup(self) -> str:
        """Erstellt Backup der Datenbank"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f"pflege_tool_backup_{timestamp}.db")
        
        shutil.copy2(self.db_path, backup_path)
        
        # Alte Backups löschen (>30 Tage)
        self._cleanup_old_backups(days=30)
        
        return backup_path
    
    def restore_backup(self, backup_path: str):
        """Stellt Backup wieder her"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup nicht gefunden: {backup_path}")
        
        # Aktuelles als Backup sichern
        self.create_backup()
        
        # Backup wiederherstellen
        shutil.copy2(backup_path, self.db_path)
    
    def _cleanup_old_backups(self, days: int = 30):
        """Löscht alte Backups"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_date:
                    os.remove(filepath)
    
    def export_to_json(self, output_path: str):
        """Exportiert alle Daten als JSON"""
        assessments = self.get_all_assessments(limit=10000)
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'assessments': assessments
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def get_statistics(self) -> Dict:
        """Statistiken für Dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Anzahl Assessments
        cursor.execute("SELECT COUNT(*) FROM assessments")
        stats['total_assessments'] = cursor.fetchone()[0]
        
        # MDK-Ready Quote
        cursor.execute("SELECT COUNT(*) FROM assessments WHERE mdk_ready = 1")
        mdk_ready = cursor.fetchone()[0]
        stats['mdk_ready_count'] = mdk_ready
        stats['mdk_ready_percentage'] = (mdk_ready / stats['total_assessments'] * 100) if stats['total_assessments'] > 0 else 0
        
        # FEM-Alerts
        cursor.execute("SELECT COUNT(DISTINCT assessment_id) FROM fem_alerts")
        stats['fem_alerts_count'] = cursor.fetchone()[0]
        
        # Durchschnittlicher Compliance-Score
        cursor.execute("SELECT AVG(compliance_score) FROM assessments")
        stats['avg_compliance_score'] = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return stats

# ============================================================================
# INTEGRATION IN STREAMLIT
# ============================================================================

# In main() am Anfang hinzufügen:

def init_database():
    """Initialisiert Datenbank"""
    if 'db_manager' not in st.session_state:
        st.session_state['db_manager'] = DatabaseManager()
        
        # Migration: Session State → Database
        if 'assessments_history' in st.session_state:
            for assessment in st.session_state['assessments_history']:
                try:
                    st.session_state['db_manager'].save_assessment(assessment)
                except ValueError:
                    pass  # Bereits vorhanden
