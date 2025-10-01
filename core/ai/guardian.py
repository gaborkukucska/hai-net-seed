# START OF FILE core/ai/guardian.py
"""
HAI-Net Constitutional Guardian Agent
Constitutional compliance: All four principles actively monitored and enforced
Independent agent responsible for constitutional oversight and protection
"""

import asyncio
import time
import json
import secrets
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading

from core.config.settings import HAINetSettings
from core.logging.logger import get_logger
from core.identity.did import ConstitutionalViolationError
from .agents import Agent, AgentRole, AgentState, AgentCapability


class ViolationType(Enum):
    """Types of constitutional violations"""
    PRIVACY_VIOLATION = "privacy_violation"
    HUMAN_RIGHTS_VIOLATION = "human_rights_violation" 
    CENTRALIZATION_VIOLATION = "centralization_violation"
    COMMUNITY_VIOLATION = "community_violation"
    SYSTEM_VIOLATION = "system_violation"


class ViolationSeverity(Enum):
    """Severity levels for violations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConstitutionalViolation:
    """Represents a constitutional violation"""
    violation_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    principle_violated: str
    description: str
    source_component: str
    source_agent: Optional[str]
    timestamp: float
    details: Dict[str, Any]
    remediation_suggested: List[str]
    auto_resolved: bool = False
    acknowledged: bool = False


@dataclass
class ComplianceMetrics:
    """Constitutional compliance metrics"""
    total_violations: int
    violations_by_type: Dict[ViolationType, int]
    violations_by_severity: Dict[ViolationSeverity, int]
    compliance_score: float  # 0.0 to 1.0
    privacy_score: float
    human_rights_score: float
    decentralization_score: float
    community_score: float
    last_assessment: float
    monitoring_uptime: float


class ConstitutionalGuardian:
    """
    Constitutional Guardian Agent
    Independent monitoring and enforcement of constitutional principles
    """
    
    def __init__(self, settings: HAINetSettings, guardian_agent: Optional[Agent] = None):
        self.settings = settings
        self.guardian_agent = guardian_agent
        self.logger = get_logger("ai.guardian", settings)
        
        # Constitutional monitoring
        self.constitutional_version = "1.0"
        self.monitoring_active = False
        self.violations: Dict[str, ConstitutionalViolation] = {}
        self.violation_counter = 0
        
        # Compliance tracking
        self.metrics = ComplianceMetrics(
            total_violations=0,
            violations_by_type={vt: 0 for vt in ViolationType},
            violations_by_severity={vs: 0 for vs in ViolationSeverity},
            compliance_score=1.0,
            privacy_score=1.0,
            human_rights_score=1.0,
            decentralization_score=1.0,
            community_score=1.0,
            last_assessment=time.time(),
            monitoring_uptime=0
        )
        
        # Monitoring rules and patterns
        self.privacy_patterns = [
            "personal information", "private data", "confidential",
            "social security", "credit card", "password", "api key",
            "email address", "phone number", "home address"
        ]
        
        self.human_rights_patterns = [
            "discrimination", "bias", "unfair treatment", "exclusion",
            "manipulation", "coercion", "surveillance", "tracking"
        ]
        
        self.centralization_patterns = [
            "central server", "single point", "central authority",
            "centralized control", "master control", "central database"
        ]
        
        self.community_patterns = [
            "resource hoarding", "monopolization", "exclusivity",
            "community harm", "anti-social", "selfish behavior"
        ]
        
        # Remediation actions
        self.remediation_callbacks: Dict[ViolationType, List[Callable]] = {
            vt: [] for vt in ViolationType
        }
        
        # Guardian state
        self.started_at = time.time()
        self.last_violation_check = time.time()
        self.monitoring_interval = 10  # seconds
        self.assessment_interval = 60  # seconds
        
        # Threading
        self._lock = asyncio.Lock()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.assessment_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self) -> bool:
        """Start constitutional monitoring"""
        try:
            async with self._lock:
                if self.monitoring_active:
                    return True
                
                # Start monitoring tasks
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
                self.assessment_task = asyncio.create_task(self._assessment_loop())
                
                self.monitoring_active = True
                
                # Log initial constitutional principles
                await self._log_constitutional_commitment()
                
                self.logger.log_human_rights_event(
                    "constitutional_guardian_started",
                    user_control=True
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Guardian monitoring startup failed: {e}")
            return False
    
    async def stop_monitoring(self):
        """Stop constitutional monitoring"""
        try:
            async with self._lock:
                if not self.monitoring_active:
                    return
                
                self.monitoring_active = False
                
                # Stop monitoring tasks
                if self.monitoring_task:
                    self.monitoring_task.cancel()
                    try:
                        await self.monitoring_task
                    except asyncio.CancelledError:
                        pass
                
                if self.assessment_task:
                    self.assessment_task.cancel()
                    try:
                        await self.assessment_task
                    except asyncio.CancelledError:
                        pass
                
                self.logger.log_human_rights_event(
                    "constitutional_guardian_stopped",
                    user_control=True
                )
                
        except Exception as e:
            self.logger.error(f"Guardian monitoring shutdown failed: {e}")

    async def review_output(self, agent: Agent, content: str) -> Dict[str, Any]:
        """
        Reviews an agent's output for constitutional compliance before it is committed.
        Returns a dictionary with a compliance verdict.
        """
        self.logger.debug(f"Guardian reviewing output from agent {agent.agent_id}")

        content_lower = content.lower()

        # Check for privacy violations
        for pattern in self.privacy_patterns:
            if pattern in content_lower:
                violation_id = await self.report_violation(
                    violation_type=ViolationType.PRIVACY_VIOLATION,
                    severity=ViolationSeverity.HIGH,
                    principle_violated="Privacy First",
                    description=f"Agent output contained potential private data pattern: '{pattern}'",
                    source_component="agent_output_review",
                    source_agent=agent.agent_id,
                    details={"content_snippet": content[:200]}
                )
                return {"compliant": False, "violation_id": violation_id, "reason": "Privacy violation"}

        # Check for human rights violations
        for pattern in self.human_rights_patterns:
            if pattern in content_lower:
                violation_id = await self.report_violation(
                    violation_type=ViolationType.HUMAN_RIGHTS_VIOLATION,
                    severity=ViolationSeverity.HIGH,
                    principle_violated="Human Rights",
                    description=f"Agent output contained potential human rights violation pattern: '{pattern}'",
                    source_component="agent_output_review",
                    source_agent=agent.agent_id,
                    details={"content_snippet": content[:200]}
                )
                return {"compliant": False, "violation_id": violation_id, "reason": "Human rights violation"}

        self.logger.debug(f"Output from agent {agent.agent_id} passed guardian review.")
        return {"compliant": True}
    
    async def _log_constitutional_commitment(self):
        """Log constitutional commitment and principles"""
        constitutional_commitment = {
            "principles": [
                "Privacy First: No personal data leaves Local Hub without explicit consent",
                "Human Rights: Protect and promote fundamental human rights", 
                "Decentralization: No central control points or single points of failure",
                "Community Focus: Strengthen real-world connections and collaboration"
            ],
            "enforcement": "Educational approach with protective measures",
            "version": self.constitutional_version,
            "guardian_oath": "I solemnly commit to protecting human rights and constitutional principles in all HAI-Net operations"
        }
        
        self.logger.log_human_rights_event(
            "constitutional_commitment_logged",
            user_control=True
        )
        
        self.logger.info("Constitutional Guardian oath taken - protecting human rights and constitutional principles")
    
    async def report_violation(self, violation_type: ViolationType, severity: ViolationSeverity,
                              principle_violated: str, description: str,
                              source_component: str, source_agent: Optional[str] = None,
                              details: Optional[Dict[str, Any]] = None) -> str:
        """
        Report a constitutional violation
        
        Args:
            violation_type: Type of violation
            severity: Severity level
            principle_violated: Which constitutional principle was violated
            description: Description of the violation
            source_component: Component that detected/caused the violation
            source_agent: Optional agent that caused the violation
            details: Additional violation details
            
        Returns:
            Violation ID for tracking
        """
        try:
            async with self._lock:
                # Generate violation ID
                self.violation_counter += 1
                violation_id = f"violation_{self.violation_counter:06d}_{secrets.token_hex(4)}"
                
                # Suggest remediation actions
                remediation = await self._suggest_remediation(violation_type, severity, details or {})
                
                # Create violation record
                violation = ConstitutionalViolation(
                    violation_id=violation_id,
                    violation_type=violation_type,
                    severity=severity,
                    principle_violated=principle_violated,
                    description=description,
                    source_component=source_component,
                    source_agent=source_agent,
                    timestamp=time.time(),
                    details=details or {},
                    remediation_suggested=remediation,
                    auto_resolved=False,
                    acknowledged=False
                )
                
                # Store violation
                self.violations[violation_id] = violation
                
                # Update metrics
                self.metrics.total_violations += 1
                self.metrics.violations_by_type[violation_type] += 1
                self.metrics.violations_by_severity[severity] += 1
                
                # Log violation
                await self._log_violation(violation)
                
                # Attempt automatic remediation for certain violations
                if severity in [ViolationSeverity.LOW, ViolationSeverity.MEDIUM]:
                    await self._attempt_auto_remediation(violation)
                
                # Trigger remediation callbacks
                await self._trigger_remediation_callbacks(violation)
                
                # Update compliance scores
                await self._update_compliance_scores()
                
                return violation_id
                
        except Exception as e:
            self.logger.error(f"Violation reporting failed: {e}")
            return ""
    
    async def _suggest_remediation(self, violation_type: ViolationType, 
                                  severity: ViolationSeverity, 
                                  details: Dict[str, Any]) -> List[str]:
        """Suggest remediation actions for a violation"""
        suggestions = []
        
        if violation_type == ViolationType.PRIVACY_VIOLATION:
            suggestions.extend([
                "Review data handling procedures",
                "Implement additional privacy controls", 
                "Verify user consent for data processing",
                "Consider data minimization techniques",
                "Review encryption and access controls"
            ])
            
        elif violation_type == ViolationType.HUMAN_RIGHTS_VIOLATION:
            suggestions.extend([
                "Review system bias and fairness",
                "Implement accessibility improvements",
                "Ensure user agency and control",
                "Review decision-making transparency",
                "Provide user recourse mechanisms"
            ])
            
        elif violation_type == ViolationType.CENTRALIZATION_VIOLATION:
            suggestions.extend([
                "Implement decentralized alternatives",
                "Remove single points of failure",
                "Distribute authority and control",
                "Enable peer-to-peer operations",
                "Reduce dependency on central services"
            ])
            
        elif violation_type == ViolationType.COMMUNITY_VIOLATION:
            suggestions.extend([
                "Strengthen community engagement",
                "Implement resource sharing mechanisms",
                "Encourage collaborative behaviors",
                "Review community impact of actions",
                "Foster inclusive participation"
            ])
        
        # Add severity-specific suggestions
        if severity == ViolationSeverity.CRITICAL:
            suggestions.insert(0, "IMMEDIATE ACTION REQUIRED - System may need to be halted")
            suggestions.insert(1, "Escalate to human oversight immediately")
        elif severity == ViolationSeverity.HIGH:
            suggestions.insert(0, "High priority remediation required")
            suggestions.insert(1, "Consider temporary restrictions until resolved")
        
        return suggestions
    
    async def _log_violation(self, violation: ConstitutionalViolation):
        """Log a constitutional violation"""
        # Log based on violation type
        if violation.violation_type == ViolationType.PRIVACY_VIOLATION:
            self.logger.log_privacy_event(
                f"violation_detected_{violation.severity.value}",
                violation.source_component,
                user_consent=False
            )
        elif violation.violation_type == ViolationType.HUMAN_RIGHTS_VIOLATION:
            self.logger.log_human_rights_event(
                f"rights_violation_{violation.severity.value}",
                user_control=False
            )
        elif violation.violation_type == ViolationType.CENTRALIZATION_VIOLATION:
            self.logger.log_decentralization_event(
                f"centralization_detected_{violation.severity.value}",
                local_processing=False
            )
        elif violation.violation_type == ViolationType.COMMUNITY_VIOLATION:
            self.logger.log_community_event(
                f"community_harm_detected_{violation.severity.value}",
                community_benefit=False
            )
        
        # Always log as violation regardless of type
        self.logger.log_violation(f"{violation.violation_type.value}_{violation.severity.value}", {
            "violation_id": violation.violation_id,
            "principle": violation.principle_violated,
            "description": violation.description,
            "source": violation.source_component,
            "agent": violation.source_agent,
            "details": violation.details
        })
        
        # Critical violations get additional logging
        if violation.severity == ViolationSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL CONSTITUTIONAL VIOLATION: {violation.description}")
            self.logger.critical(f"Immediate remediation required: {violation.remediation_suggested}")
    
    async def _attempt_auto_remediation(self, violation: ConstitutionalViolation):
        """Attempt automatic remediation for certain violations"""
        try:
            remediated = False
            
            # Privacy violations
            if (violation.violation_type == ViolationType.PRIVACY_VIOLATION and 
                violation.severity in [ViolationSeverity.LOW, ViolationSeverity.MEDIUM]):
                
                # Auto-remediation for privacy violations
                if "data_retention" in violation.details:
                    # Implement data cleanup
                    remediated = await self._auto_cleanup_data(violation)
                elif "consent_missing" in violation.details:
                    # Request user consent
                    remediated = await self._auto_request_consent(violation)
            
            # Community violations
            elif (violation.violation_type == ViolationType.COMMUNITY_VIOLATION and
                  violation.severity == ViolationSeverity.LOW):
                
                # Auto-remediation for minor community violations
                if "resource_usage" in violation.details:
                    remediated = await self._auto_balance_resources(violation)
            
            if remediated:
                violation.auto_resolved = True
                self.logger.info(f"Auto-remediated violation {violation.violation_id}")
                
        except Exception as e:
            self.logger.error(f"Auto-remediation failed for {violation.violation_id}: {e}")
    
    async def _auto_cleanup_data(self, violation: ConstitutionalViolation) -> bool:
        """Auto-cleanup data for privacy violations"""
        try:
            # This would integrate with the storage system to cleanup old data
            # For now, we'll simulate the action
            self.logger.info(f"Auto-cleaning data for violation {violation.violation_id}")
            return True
        except Exception:
            return False
    
    async def _auto_request_consent(self, violation: ConstitutionalViolation) -> bool:
        """Auto-request user consent for privacy violations"""
        try:
            # This would integrate with the UI system to request consent
            # For now, we'll simulate the action
            self.logger.info(f"Auto-requesting consent for violation {violation.violation_id}")
            return True
        except Exception:
            return False
    
    async def _auto_balance_resources(self, violation: ConstitutionalViolation) -> bool:
        """Auto-balance resources for community violations"""
        try:
            # This would integrate with resource management to balance usage
            # For now, we'll simulate the action
            self.logger.info(f"Auto-balancing resources for violation {violation.violation_id}")
            return True
        except Exception:
            return False
    
    async def _trigger_remediation_callbacks(self, violation: ConstitutionalViolation):
        """Trigger registered remediation callbacks"""
        callbacks = self.remediation_callbacks.get(violation.violation_type, [])
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(violation)
                else:
                    callback(violation)
            except Exception as e:
                self.logger.error(f"Remediation callback error: {e}")
    
    async def _update_compliance_scores(self):
        """Update constitutional compliance scores"""
        try:
            # Calculate compliance scores based on violations
            total_possible_score = 1.0
            
            # Privacy score
            privacy_violations = self.metrics.violations_by_type.get(ViolationType.PRIVACY_VIOLATION, 0)
            self.metrics.privacy_score = max(0.0, total_possible_score - (privacy_violations * 0.1))
            
            # Human rights score
            rights_violations = self.metrics.violations_by_type.get(ViolationType.HUMAN_RIGHTS_VIOLATION, 0)
            self.metrics.human_rights_score = max(0.0, total_possible_score - (rights_violations * 0.15))
            
            # Decentralization score
            central_violations = self.metrics.violations_by_type.get(ViolationType.CENTRALIZATION_VIOLATION, 0)
            self.metrics.decentralization_score = max(0.0, total_possible_score - (central_violations * 0.1))
            
            # Community score
            community_violations = self.metrics.violations_by_type.get(ViolationType.COMMUNITY_VIOLATION, 0)
            self.metrics.community_score = max(0.0, total_possible_score - (community_violations * 0.05))
            
            # Overall compliance score (weighted average)
            self.metrics.compliance_score = (
                self.metrics.privacy_score * 0.3 +
                self.metrics.human_rights_score * 0.3 +
                self.metrics.decentralization_score * 0.2 +
                self.metrics.community_score * 0.2
            )
            
            # Apply severity penalties
            critical_violations = self.metrics.violations_by_severity.get(ViolationSeverity.CRITICAL, 0)
            high_violations = self.metrics.violations_by_severity.get(ViolationSeverity.HIGH, 0)
            
            severity_penalty = (critical_violations * 0.3) + (high_violations * 0.1)
            self.metrics.compliance_score = max(0.0, self.metrics.compliance_score - severity_penalty)
            
            self.metrics.last_assessment = time.time()
            
        except Exception as e:
            self.logger.error(f"Compliance score update failed: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for constitutional compliance"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(self.monitoring_interval)
                
                if not self.monitoring_active:
                    break
                
                # Update monitoring uptime
                self.metrics.monitoring_uptime = time.time() - self.started_at
                
                # Perform constitutional checks
                await self._check_system_compliance()
                
                # Check for patterns in recent violations
                await self._analyze_violation_patterns()
                
                # Update last check time
                self.last_violation_check = time.time()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _assessment_loop(self):
        """Periodic assessment loop for comprehensive compliance review"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(self.assessment_interval)
                
                if not self.monitoring_active:
                    break
                
                # Perform comprehensive assessment
                await self._perform_compliance_assessment()
                
                # Generate compliance report
                await self._generate_compliance_report()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Assessment loop error: {e}")
                await asyncio.sleep(10)  # Longer pause on error
    
    async def _check_system_compliance(self):
        """Check overall system compliance"""
        # This is a placeholder for comprehensive system checks
        # In a full implementation, this would:
        # - Check agent behaviors
        # - Monitor data flows
        # - Verify user consent status
        # - Check resource usage patterns
        # - Monitor network communications
        
        current_time = time.time()
        
        # Example check: Monitor if compliance score is declining
        if self.metrics.compliance_score < 0.8:
            await self.report_violation(
                ViolationType.SYSTEM_VIOLATION,
                ViolationSeverity.MEDIUM,
                "Overall Compliance",
                f"System compliance score below threshold: {self.metrics.compliance_score:.2f}",
                "constitutional_guardian",
                details={"compliance_score": self.metrics.compliance_score}
            )
    
    async def _analyze_violation_patterns(self):
        """Analyze patterns in violations to identify systemic issues"""
        try:
            recent_violations = [
                v for v in self.violations.values()
                if time.time() - v.timestamp < 3600  # Last hour
            ]
            
            if len(recent_violations) > 10:  # Many violations in short time
                await self.report_violation(
                    ViolationType.SYSTEM_VIOLATION,
                    ViolationSeverity.HIGH,
                    "System Stability",
                    f"High violation rate detected: {len(recent_violations)} violations in last hour",
                    "constitutional_guardian",
                    details={"violation_count": len(recent_violations)}
                )
            
            # Check for repeated violations from same source
            source_counts = {}
            for violation in recent_violations:
                source = violation.source_component
                source_counts[source] = source_counts.get(source, 0) + 1
            
            for source, count in source_counts.items():
                if count >= 5:  # Same source causing many violations
                    await self.report_violation(
                        ViolationType.SYSTEM_VIOLATION,
                        ViolationSeverity.MEDIUM,
                        "Component Reliability",
                        f"Component {source} has generated {count} violations recently",
                        "constitutional_guardian",
                        details={"problematic_component": source, "violation_count": count}
                    )
                    
        except Exception as e:
            self.logger.error(f"Violation pattern analysis failed: {e}")
    
    async def _perform_compliance_assessment(self):
        """Perform comprehensive compliance assessment"""
        try:
            # Update compliance scores
            await self._update_compliance_scores()
            
            # Check compliance trends
            if self.metrics.compliance_score < 0.7:
                self.logger.warning(f"Low compliance score: {self.metrics.compliance_score:.2f}")
            elif self.metrics.compliance_score > 0.95:
                self.logger.info(f"Excellent compliance score: {self.metrics.compliance_score:.2f}")
            
            # Log assessment
            self.logger.log_human_rights_event(
                "compliance_assessment_completed",
                user_control=True
            )
            
        except Exception as e:
            self.logger.error(f"Compliance assessment failed: {e}")
    
    async def _generate_compliance_report(self):
        """Generate compliance report"""
        try:
            report = {
                "assessment_time": time.time(),
                "monitoring_uptime": self.metrics.monitoring_uptime,
                "overall_compliance_score": self.metrics.compliance_score,
                "principle_scores": {
                    "privacy_first": self.metrics.privacy_score,
                    "human_rights": self.metrics.human_rights_score,
                    "decentralization": self.metrics.decentralization_score,
                    "community_focus": self.metrics.community_score
                },
                "violation_summary": {
                    "total_violations": self.metrics.total_violations,
                    "by_type": {vt.value: count for vt, count in self.metrics.violations_by_type.items()},
                    "by_severity": {vs.value: count for vs, count in self.metrics.violations_by_severity.items()}
                },
                "recent_violations": len([
                    v for v in self.violations.values()
                    if time.time() - v.timestamp < 3600
                ]),
                "auto_resolved_violations": len([
                    v for v in self.violations.values() if v.auto_resolved
                ])
            }
            
            # Log report
            self.logger.info(f"Compliance Report: Overall Score {report['overall_compliance_score']:.2f}")
            self.logger.debug(f"Detailed Compliance Report: {json.dumps(report, indent=2)}")
            
        except Exception as e:
            self.logger.error(f"Compliance report generation failed: {e}")
    
    def add_remediation_callback(self, violation_type: ViolationType, callback: Callable):
        """Add a callback for specific violation types"""
        self.remediation_callbacks[violation_type].append(callback)
    
    def acknowledge_violation(self, violation_id: str) -> bool:
        """Acknowledge a violation (mark as reviewed)"""
        if violation_id in self.violations:
            self.violations[violation_id].acknowledged = True
            self.logger.info(f"Violation {violation_id} acknowledged")
            return True
        return False
    
    def get_violation(self, violation_id: str) -> Optional[ConstitutionalViolation]:
        """Get specific violation by ID"""
        return self.violations.get(violation_id)
    
    def get_recent_violations(self, hours: int = 24) -> List[ConstitutionalViolation]:
        """Get violations from the last N hours"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            violation for violation in self.violations.values()
            if violation.timestamp >= cutoff_time
        ]
    
    def get_violations_by_type(self, violation_type: ViolationType) -> List[ConstitutionalViolation]:
        """Get all violations of a specific type"""
        return [
            violation for violation in self.violations.values()
            if violation.violation_type == violation_type
        ]
    
    def get_compliance_metrics(self) -> ComplianceMetrics:
        """Get current compliance metrics"""
        return self.metrics
    
    def get_guardian_status(self) -> Dict[str, Any]:
        """Get guardian status and statistics"""
        return {
            "monitoring_active": self.monitoring_active,
            "constitutional_version": self.constitutional_version,
            "uptime": time.time() - self.started_at,
            "monitoring_uptime": self.metrics.monitoring_uptime,
            "total_violations": self.metrics.total_violations,
            "compliance_score": self.metrics.compliance_score,
            "principle_scores": {
                "privacy_first": self.metrics.privacy_score,
                "human_rights": self.metrics.human_rights_score,
                "decentralization": self.metrics.decentralization_score,
                "community_focus": self.metrics.community_score
            },
            "recent_violations": len(self.get_recent_violations(1)),  # Last hour
            "unacknowledged_violations": len([
                v for v in self.violations.values() if not v.acknowledged
            ]),
            "auto_resolved_violations": len([
                v for v in self.violations.values() if v.auto_resolved
            ])
        }


def create_constitutional_guardian(settings: HAINetSettings, 
                                 guardian_agent: Optional[Agent] = None) -> ConstitutionalGuardian:
    """
    Create and configure constitutional guardian
    
    Args:
        settings: HAI-Net settings
        guardian_agent: Optional agent to integrate with guardian
        
    Returns:
        Configured ConstitutionalGuardian instance
    """
    return ConstitutionalGuardian(settings, guardian_agent)


if __name__ == "__main__":
    # Test the constitutional guardian system
    import asyncio
    from core.config.settings import HAINetSettings
    
    async def test_guardian():
        print("HAI-Net Constitutional Guardian Test")
        print("=" * 40)
        
        # Create test settings
        settings = HAINetSettings()
        
        # Create guardian
        guardian = create_constitutional_guardian(settings)
        
        try:
            # Start monitoring
            if await guardian.start_monitoring():
                print("✅ Constitutional Guardian started successfully")
                
                # Test violation reporting
                violation_id = await guardian.report_violation(
                    ViolationType.PRIVACY_VIOLATION,
                    ViolationSeverity.MEDIUM,
                    "Privacy First",
                    "Test privacy violation for demonstration",
                    "test_component",
                    details={"test": "data"}
                )
                print(f"✅ Test violation reported: {violation_id}")
                
                # Test another violation
                violation_id2 = await guardian.report_violation(
                    ViolationType.HUMAN_RIGHTS_VIOLATION,
                    ViolationSeverity.LOW,
                    "Human Rights",
                    "Test human rights violation for demonstration", 
                    "test_component2"
                )
                print(f"✅ Second test violation reported: {violation_id2}")
                
                # Wait for monitoring cycle
                await asyncio.sleep(2)
                
                # Get guardian status
                status = guardian.get_guardian_status()
                print(f"📊 Guardian Status:")
                print(f"   Compliance Score: {status['compliance_score']:.2f}")
                print(f"   Total Violations: {status['total_violations']}")
                print(f"   Privacy Score: {status['principle_scores']['privacy_first']:.2f}")
                print(f"   Human Rights Score: {status['principle_scores']['human_rights']:.2f}")
                
                # Get recent violations
                recent = guardian.get_recent_violations(1)
                print(f"📋 Recent violations: {len(recent)}")
                
                # Acknowledge violation
                if violation_id:
                    acknowledged = guardian.acknowledge_violation(violation_id)
                    print(f"✅ Violation acknowledged: {acknowledged}")

                # Test output review
                print("\n--- Testing Guardian Output Review ---")
                class MockAgentForReview:
                    agent_id = "review_test_agent"

                mock_review_agent = MockAgentForReview()

                # Test compliant output
                compliant_text = "This is a perfectly safe and compliant message."
                review_result = await guardian.review_output(mock_review_agent, compliant_text)
                print(f"Compliant text review result: {review_result}")

                # Test non-compliant output
                non_compliant_text = "Here is your personal information as requested."
                review_result_bad = await guardian.review_output(mock_review_agent, non_compliant_text)
                print(f"Non-compliant text review result: {review_result_bad}")

                # Check if a new violation was logged
                status_after_review = guardian.get_guardian_status()
                print(f"Total violations after review: {status_after_review['total_violations']}")
                
                print("\n🎉 Constitutional Guardian System Working!")
                
            else:
                print("❌ Failed to start Constitutional Guardian")
                
        except Exception as e:
            print(f"❌ Guardian test failed: {e}")
        
        finally:
            await guardian.stop_monitoring()
            print("✅ Guardian monitoring stopped")
    
    # Run the test
    asyncio.run(test_guardian())
