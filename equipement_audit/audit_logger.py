"""
Élysia - Audit Logger
=====================
LVMH · Sustainable IT Intelligence

Enterprise-grade audit logging for compliance and debugging.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuditLogger:
    """Enterprise-grade audit logging for Élysia."""
    
    def __init__(self, log_dir: str = "./logs"):
        """Initialize audit logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        self.logger = logging.getLogger("elysia_audit")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        
        log_file = self.log_dir / f"elysia_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, data: Dict[str, Any], severity: str = "INFO"):
        """Log an event with full context."""
        event_record = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "severity": severity,
            "data": data
        }
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(json.dumps(event_record))
    
    def log_fleet_upload(self, filename: str, row_count: int, valid_rows: int, 
                        errors: List[str]):
        """Log fleet CSV upload event."""
        self.log_event("fleet_upload", {
            "filename": filename,
            "row_count": row_count,
            "valid_rows": valid_rows,
            "error_count": len(errors),
            "errors": errors[:10]
        }, severity="INFO" if len(errors) == 0 else "WARNING")
    
    def log_fleet_analysis(self, fleet_size: int, avg_age: float, 
                          recommendations_by_type: Dict, urgency_breakdown: Dict):
        """Log fleet analysis completion."""
        self.log_event("fleet_analysis", {
            "fleet_size": fleet_size,
            "avg_age": avg_age,
            "recommendations": recommendations_by_type,
            "urgency_breakdown": urgency_breakdown,
            "high_urgency_count": urgency_breakdown.get("HIGH", 0),
        })
    
    def log_strategy_generated(self, fleet_size: int, strategy_name: str, 
                              co2_reduction: float, annual_savings: float,
                              roi: float, target_months: int):
        """Log strategy generation."""
        self.log_event("strategy_generated", {
            "fleet_size": fleet_size,
            "strategy": strategy_name,
            "co2_reduction_pct": co2_reduction,
            "annual_savings_eur": annual_savings,
            "roi_3year": roi,
            "months_to_target": target_months,
            "achieves_target": target_months < 999
        })
    
    def log_device_analysis(self, device_name: str, age: float, persona: str,
                           recommendation: str, urgency: str, annual_savings: float):
        """Log individual device analysis."""
        self.log_event("device_analysis", {
            "device": device_name,
            "age_years": age,
            "persona": persona,
            "recommendation": recommendation,
            "urgency": urgency,
            "annual_savings": annual_savings
        })
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """Log an error with context."""
        self.log_event("error", {
            "type": error_type,
            "message": error_message,
            "context": context or {}
        }, severity="ERROR")
    
    def log_user_action(self, action: str, parameters: Dict = None):
        """Log user action."""
        self.log_event("user_action", {
            "action": action,
            "parameters": parameters or {}
        })
    
    def log_validation_error(self, validation_type: str, errors: List[str]):
        """Log validation errors."""
        self.log_event("validation_error", {
            "type": validation_type,
            "error_count": len(errors),
            "errors": errors[:20]
        }, severity="WARNING")
    
    def log_calculation(self, calculation_type: str, inputs: Dict, outputs: Dict):
        """Log detailed calculation."""
        self.log_event("calculation", {
            "type": calculation_type,
            "inputs": inputs,
            "outputs": outputs
        })
    
    def log_export(self, format_type: str, record_count: int, file_size_bytes: int):
        """Log data export."""
        self.log_event("export", {
            "format": format_type,
            "record_count": record_count,
            "file_size_kb": round(file_size_bytes / 1024, 2)
        })
    
    def log_session_start(self, session_id: Optional[str] = None):
        """Log session start."""
        self.log_event("session_start", {
            "session_id": session_id or "anonymous",
            "timestamp": datetime.now().isoformat()
        })
    
    def log_session_end(self, session_id: Optional[str] = None, 
                       duration_seconds: int = 0):
        """Log session end."""
        self.log_event("session_end", {
            "session_id": session_id or "anonymous",
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now().isoformat()
        })


# Global instance
audit_log = AuditLogger()
