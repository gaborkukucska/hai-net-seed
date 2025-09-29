# START OF FILE core/logging/constitutional_audit.py
"""
HAI-Net Constitutional Auditor
Independent monitoring and enforcement of constitutional principles
"""

import time
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from threading import Lock

from core.config.settings import HAINetSettings


class ConstitutionalPrinciple(Enum):
    """Constitutional principles that must be upheld"""
    PRIVACY_FIRST = "privacy_first"
    HUMAN_RIGHTS = "human_rights"
    DECENTRALIZATION = "decentralization"
    COMMUNITY_FOCUS = "community_focus"


class ViolationSeverity(Enum):
    """Severity levels for constitutional violations"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ConstitutionalViolation:
    """Represents a constitutional principle violation"""
    principle: ConstitutionalPrinciple
    severity: ViolationSeverity
    description: str
    timestamp: float
    component: str
    details: Dict[str, Any]
    remediation_applied: bool = False
    remediation_action: Optional[str] = None


@dataclass
class AuditEvent:
    """Represents an audit event for constitutional compliance"""
    event_type: str
    principle: ConstitutionalPrinciple
    component: str
    timestamp: float
    details: Dict[str, Any]
    compliance_status: bool


class ConstitutionalAuditor:
    """
    Independent constitutional compliance auditor
    Monitors system behavior and enforces constitutional principles
    """
    
    def __init__(self, settings: Optional[HAINetSettings] = None):
        self.settings = settings
        self.violations: List[ConstitutionalViolation] = []
        self.audit_events: List[AuditEvent] = []
        self._lock = Lock()
        self._violation_callbacks: List[Callable] = []
        self._remediation_callbacks: List[Callable] = []
        self._monitoring_active = False
        
        # Constitutional compliance metrics
        self.metrics = {
            "total_audits": 0,
            "violations_detected": 0,
            "remediations_applied": 0,
            "compliance_rate": 1.0
        }
    
    def start_monitoring(self):
        """Start constitutional monitoring"""
        with self._lock:
            self._monitoring_active = True
        
        self._log_audit_event(
            "AUDITOR_START",
            ConstitutionalPrinciple.PRIVACY_FIRST,  # Start with privacy principle
            "constitutional_auditor",
            {"monitoring_active": True}
        )
    
    def stop_monitoring(self):
        """Stop constitutional monitoring"""
        with self._lock:
            self._monitoring_active = False
        
        self._log_audit_event(
            "AUDITOR_STOP",
            ConstitutionalPrinciple.PRIVACY_FIRST,
            "constitutional_auditor",
            {"monitoring_active": False}
        )
    
    def audit_privacy_compliance(self, component: str, action: str, data_details: Dict[str, Any]) -> bool:
        """
        Audit Privacy First principle compliance (Article I)
        
        Args:
            component: Component being audited
            action: Action being performed
            data_details: Details about data handling
            
        Returns:
            True if compliant, False if violation detected
        """
        compliance_checks = [
            self._check_data_localization(data_details),
            self._check_user_consent(data_details),
            self._check_encryption_usage(data_details),
            self._check_data_minimization(data_details)
        ]
        
        is_compliant = all(compliance_checks)
        
        self._log_audit_event(
            "PRIVACY_AUDIT",
            ConstitutionalPrinciple.PRIVACY_FIRST,
            component,
            {
                "action": action,
                "compliance_checks": compliance_checks,
                "is_compliant": is_compliant,
                **data_details
            },
            is_compliant
        )
        
        if not is_compliant:
            violation = ConstitutionalViolation(
                principle=ConstitutionalPrinciple.PRIVACY_FIRST,
                severity=ViolationSeverity.CRITICAL,
                description=f"Privacy violation in {component}: {action}",
                timestamp=time.time(),
                component=component,
                details=data_details
            )
            self._record_violation(violation)
        
        return is_compliant
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Get comprehensive compliance report"""
        with self._lock:
            violation_summary = {}
            for violation in self.violations:
                principle = violation.principle.value
                violation_summary[principle] = violation_summary.get(principle, 0) + 1
            
            remediated_violations = sum(1 for v in self.violations if v.remediation_applied)
            
            return {
                "monitoring_active": self._monitoring_active,
                "total_audits": self.metrics["total_audits"],
                "violations_detected": self.metrics["violations_detected"],
                "remediations_applied": self.metrics["remediations_applied"],
                "compliance_rate": self.metrics["compliance_rate"],
                "violation_summary": violation_summary,
                "remediation_rate": remediated_violations / max(len(self.violations), 1),
                "constitutional_version": "1.0"
            }
    
    def add_violation_callback(self, callback: Callable):
        """Add callback for violation notifications"""
        self._violation_callbacks.append(callback)
    
    def add_remediation_callback(self, callback: Callable):
        """Add callback for remediation notifications"""
        self._remediation_callbacks.append(callback)
    
    # Private methods for compliance checking
    def _check_data_localization(self, data_details: Dict[str, Any]) -> bool:
        """Check if data stays local (Privacy First)"""
        return data_details.get("local_processing", True) and not data_details.get("external_transmission", False)
    
    def _check_user_consent(self, data_details: Dict[str, Any]) -> bool:
        """Check if user consent was obtained"""
        return data_details.get("user_consent", False) or data_details.get("consent_not_required", False)
    
    def _check_encryption_usage(self, data_details: Dict[str, Any]) -> bool:
        """Check if encryption is used for sensitive data"""
        return data_details.get("encrypted", True) or data_details.get("no_sensitive_data", False)
    
    def _check_data_minimization(self, data_details: Dict[str, Any]) -> bool:
        """Check if data collection is minimized"""
        return data_details.get("data_minimized", True)
    
    def _record_violation(self, violation: ConstitutionalViolation):
        """Record a constitutional violation"""
        with self._lock:
            self.violations.append(violation)
            self.metrics["violations_detected"] += 1
            self._update_compliance_rate()
        
        # Notify callbacks
        for callback in self._violation_callbacks:
            callback(violation)
    
    def _log_audit_event(self, event_type: str, principle: ConstitutionalPrinciple, 
                        component: str, details: Dict[str, Any], compliance_status: bool = True):
        """Log an audit event"""
        event = AuditEvent(
            event_type=event_type,
            principle=principle,
            component=component,
            timestamp=time.time(),
            details=details,
            compliance_status=compliance_status
        )
        
        with self._lock:
            self.audit_events.append(event)
            self.metrics["total_audits"] += 1
    
    def _update_compliance_rate(self):
        """Update the overall compliance rate"""
        total_violations = self.metrics["violations_detected"]
        total_audits = self.metrics["total_audits"]
        
        if total_audits > 0:
            self.metrics["compliance_rate"] = 1.0 - (total_violations / total_audits)
        else:
            self.metrics["compliance_rate"] = 1.0


def create_constitutional_auditor(settings: Optional[HAINetSettings] = None) -> ConstitutionalAuditor:
    """
    Factory function to create a constitutional auditor
    
    Args:
        settings: Optional HAI-Net settings
        
    Returns:
        Configured constitutional auditor
    """
    return ConstitutionalAuditor(settings)


if __name__ == "__main__":
    # Test the constitutional auditor
    print("HAI-Net Constitutional Auditor Test")
    print("=" * 40)
    
    auditor = ConstitutionalAuditor()
    auditor.start_monitoring()
    
    # Test privacy compliance audit
    print("\n🔒 Testing Privacy Compliance...")
    privacy_compliant = auditor.audit_privacy_compliance(
        "identity_system",
        "create_identity",
        {
            "local_processing": True,
            "user_consent": True,
            "encrypted": True,
            "data_minimized": True
        }
    )
    print(f"Privacy Compliant: {'✅' if privacy_compliant else '❌'}")
    
    # Get compliance report
    print("\n📊 Compliance Report:")
    report = auditor.get_compliance_report()
    print(f"Total Audits: {report['total_audits']}")
    print(f"Violations Detected: {report['violations_detected']}")
    print(f"Compliance Rate: {report['compliance_rate']:.2%}")
    
    auditor.stop_monitoring()
    print("\n✅ Constitutional Auditor Test Complete!")
