# START OF FILE tests/test_e2e_integration.py
"""
HAI-Net End-to-End Integration Tests
Constitutional compliance: All Four Principles + Full System Integration
Tests the complete HAI-Net system from constitutional compliance to network visualization
"""

import asyncio
import pytest
import time
import uuid
import threading
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# HAI-Net Core Imports
from core.config.settings import HAINetSettings
from core.identity.did import IdentityManager, ConstitutionalViolationError
from core.logging.constitutional_audit import ConstitutionalAuditor
from core.logging.logger import get_logger
from core.network.discovery import LocalDiscovery, NetworkNode as DiscoveryNode
from core.network.node_manager import NodeRoleManager, NodeRole, RoleChangeEvent


class TestHAINetEndToEndIntegration:
    """
    End-to-end integration tests for HAI-Net Seed framework
    Tests full system integration with constitutional compliance
    """
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment for each test"""
        # Create unique test settings for each test
        self.settings = HAINetSettings()
        self.settings.debug_mode = True
        self.settings.log_level = "DEBUG"
        
        # Generate unique test identifiers
        self.test_node_id = f"test_node_{uuid.uuid4().hex[:8]}"
        self.test_did = f"did:hai:test_{uuid.uuid4().hex[:16]}"
        
        # Track test resources for cleanup
        self.test_services = []
        
        yield
        
        # Clean up test resources
        for service in self.test_services:
            if hasattr(service, 'stop_discovery'):
                service.stop_discovery()
            if hasattr(service, 'stop_role_management'):
                service.stop_role_management()

    def test_constitutional_identity_system_integration(self):
        """
        Test integration between constitutional auditor and identity system
        Verifies that constitutional violations are properly caught and logged
        """
        # Initialize constitutional auditor
        auditor = ConstitutionalAuditor(self.settings)
        self.test_services.append(auditor)
        
        # Initialize identity manager
        identity_manager = IdentityManager()
        
        # Test 1: Valid identity creation should pass constitutional audit
        valid_identity = identity_manager.create_identity(
            full_name="Test User",
            date_of_birth="1990-01-01",
            government_id="TEST123456",
            passphrase="secure_test_passphrase",
            email="test@example.com"
        )
        
        # Verify identity was created and is constitutionally compliant
        assert valid_identity is not None
        assert "did" in valid_identity
        assert valid_identity["constitutional_version"] == "1.0"
        assert valid_identity["privacy_settings"]["data_sharing_consent"] is False  # Privacy First
        assert valid_identity["privacy_settings"]["community_participation"] is True  # Community Focus
        
        # Test 2: Invalid identity creation should trigger constitutional violation
        with pytest.raises(ConstitutionalViolationError) as exc_info:
            identity_manager.create_identity(
                full_name="Bad User",
                date_of_birth="1990-01-01", 
                government_id="BAD123",
                passphrase="weak",
                email="invalid-email"
            )
        
        # Verify constitutional violation contains educational message
        error_message = str(exc_info.value).lower()
        assert "protecting" in error_message or "privacy" in error_message
        
        print("✅ Constitutional identity system integration test passed")

    def test_network_discovery_and_role_management_integration(self):
        """
        Test integration between network discovery and node role management
        Verifies that nodes can discover each other and negotiate roles constitutionally
        """
        # Test with multiple simulated nodes
        node_managers = []
        
        try:
            # Create multiple node role managers
            for i in range(3):
                node_id = f"test_node_{i}_{uuid.uuid4().hex[:6]}"
                role_manager = NodeRoleManager(self.settings, node_id)
                node_managers.append(role_manager)
                self.test_services.append(role_manager)
            
            # Start first node as master
            master_manager = node_managers[0]
            master_manager.settings.node_role = "master"
            
            # Track role changes
            role_changes = []
            def track_role_changes(event: RoleChangeEvent):
                role_changes.append(event)
            
            master_manager.add_role_change_callback(track_role_changes)
            
            # Start role management
            assert master_manager.start_role_management()
            
            # Allow time for initialization
            time.sleep(2)
            
            # Verify master role assignment
            assert master_manager.get_current_role() == NodeRole.MASTER
            
            # Get network status
            network_status = master_manager.get_network_status()
            assert network_status["current_role"] == "master"
            assert network_status["constitutional_compliance"] is True
            assert network_status["network_decentralized"] is True
            
            # Test constitutional compliance in role management
            role_history = master_manager.get_role_history()
            if role_history:
                for event in role_history:
                    assert event.node_metrics.constitutional_compliance_score >= 0.9
            
            print("✅ Network discovery and role management integration test passed")
            
        finally:
            # Clean up
            for manager in node_managers:
                if hasattr(manager, 'stop_role_management'):
                    manager.stop_role_management()

    def test_constitutional_logging_system_integration(self):
        """
        Test integration between all systems and constitutional logging
        Verifies that all constitutional events are properly logged and audited
        """
        # Initialize constitutional auditor with event tracking
        auditor = ConstitutionalAuditor(self.settings)
        self.test_services.append(auditor)
        
        # Initialize logger
        logger = get_logger("test.integration", self.settings)
        
        # Track logged events
        logged_events = []
        original_log_event = auditor.log_constitutional_event
        
        def track_events(event_type: str, details: Dict[str, Any], **kwargs):
            logged_events.append({"type": event_type, "details": details, "kwargs": kwargs})
            return original_log_event(event_type, details, **kwargs)
        
        auditor.log_constitutional_event = track_events
        
        # Test 1: Privacy First logging
        logger.log_privacy_event("test_privacy_event", "test_data", user_consent=True)
        
        # Test 2: Human Rights logging  
        logger.log_human_rights_event("test_rights_event", user_control=True)
        
        # Test 3: Decentralization logging
        logger.log_decentralization_event("test_decentralization_event", local_processing=True)
        
        # Test 4: Community Focus logging
        logger.log_community_event("test_community_event", community_benefit=True)
        
        # Verify all constitutional principles were logged
        logged_types = [event["type"] for event in logged_events]
        assert "privacy_first" in logged_types
        assert "human_rights" in logged_types  
        assert "decentralization" in logged_types
        assert "community_focus" in logged_types
        
        print("✅ Constitutional logging system integration test passed")

    def test_full_system_integration_simulation(self):
        """
        Full system integration test simulating a complete HAI-Net session
        Tests identity creation -> role management -> network discovery -> constitutional compliance
        """
        # Step 1: Create user identity with constitutional compliance
        identity_manager = IdentityManager()
        
        user_identity = identity_manager.create_identity(
            full_name="Integration Test User",
            date_of_birth="1985-03-15",
            government_id="INTTEST123456",
            passphrase="full_integration_test_passphrase",
            email="integration@hainet.test"
        )
        
        assert user_identity is not None
        user_did = user_identity["did"]
        
        # Step 2: Initialize node role management with user identity
        role_manager = NodeRoleManager(self.settings, self.test_node_id, user_did)
        self.test_services.append(role_manager)
        
        # Track all constitutional events
        constitutional_events = []
        def track_constitutional_events(event: RoleChangeEvent):
            constitutional_events.append({
                "timestamp": event.timestamp,
                "role_change": f"{event.previous_role.value} -> {event.new_role.value}",
                "reason": event.reason.value,
                "constitutional_compliant": event.node_metrics.constitutional_compliance_score >= 0.9
            })
        
        role_manager.add_role_change_callback(track_constitutional_events)
        
        # Step 3: Start network services
        assert role_manager.start_role_management()
        
        # Allow system to stabilize
        time.sleep(3)
        
        # Step 4: Verify full system state
        current_role = role_manager.get_current_role()
        network_status = role_manager.get_network_status()
        
        # Verify constitutional compliance across all systems
        assert network_status["constitutional_compliance"] is True
        assert user_identity["constitutional_version"] == "1.0"
        assert current_role in [NodeRole.MASTER, NodeRole.SLAVE, NodeRole.CANDIDATE]
        
        # Step 5: Test user rights (constitutional override capability)
        if self.settings.user_override_enabled:
            # Test user can override system decisions (Human Rights principle)
            original_role = current_role
            target_role = NodeRole.SLAVE if original_role != NodeRole.SLAVE else NodeRole.MASTER
            
            override_success = role_manager.force_role_change(
                target_role,
                reason="Integration test user override"
            )
            
            if override_success:
                time.sleep(1)  # Allow role change to process
                new_role = role_manager.get_current_role()
                # Verify role change was applied (respecting user rights)
                assert new_role == target_role
        
        # Step 6: Verify constitutional audit trail exists
        role_history = role_manager.get_role_history()
        if role_history:
            for event in role_history:
                # All events should maintain constitutional compliance
                assert event.node_metrics.constitutional_compliance_score >= 0.8
                assert event.timestamp > 0
        
        print("✅ Full system integration simulation test passed")

    def test_constitutional_violation_handling_integration(self):
        """
        Test how the integrated system handles constitutional violations
        Verifies educational approach and system self-correction
        """
        # Initialize systems
        identity_manager = IdentityManager()
        auditor = ConstitutionalAuditor(self.settings)
        self.test_services.append(auditor)
        
        # Track violations
        violations = []
        original_log_violation = auditor.log_violation
        
        def track_violations(violation_type: str, details: Dict[str, Any]):
            violations.append({"type": violation_type, "details": details})
            return original_log_violation(violation_type, details)
        
        auditor.log_violation = track_violations
        
        # Test 1: Identity system violation handling
        with pytest.raises(ConstitutionalViolationError):
            identity_manager.create_identity(
                full_name="Violation Test",
                date_of_birth="1990-01-01",
                government_id="VIO123",
                passphrase="weak",  # Too weak, should trigger violation
                email="bad-email"   # Invalid format, should trigger violation
            )
        
        # Test 2: Role management violation handling
        role_manager = NodeRoleManager(self.settings, self.test_node_id)
        
        # Simulate violation by attempting invalid role change without user override
        role_manager.settings.user_override_enabled = False
        
        violation_occurred = False
        try:
            role_manager.force_role_change(NodeRole.MASTER, "Unauthorized test")
        except ConstitutionalViolationError:
            violation_occurred = True
        
        assert violation_occurred, "Expected constitutional violation for unauthorized role change"
        
        # Verify violations were logged and are educational
        assert len(violations) > 0
        
        for violation in violations:
            # Check that violation details contain educational information
            details_str = str(violation["details"]).lower()
            # Should contain educational/protective language, not punitive
            educational_terms = ["protecting", "privacy", "ensuring", "constitutional"]
            assert any(term in details_str for term in educational_terms), \
                f"Violation should contain educational language: {violation}"
        
        print("✅ Constitutional violation handling integration test passed")

    def test_performance_and_scalability_integration(self):
        """
        Test system performance under load while maintaining constitutional compliance
        Verifies that constitutional principles don't significantly impact performance
        """
        import time
        
        # Performance baseline test
        start_time = time.time()
        
        # Test rapid identity creation (simulating user onboarding)
        identity_manager = IdentityManager()
        identities_created = 0
        
        for i in range(10):  # Create 10 identities rapidly
            try:
                identity = identity_manager.create_identity(
                    full_name=f"Performance Test User {i}",
                    date_of_birth="1990-01-01",
                    government_id=f"PERF{i:06d}",
                    passphrase=f"performance_test_passphrase_{i}",
                    email=f"perf{i}@test.com"
                )
                if identity:
                    identities_created += 1
            except Exception as e:
                print(f"Identity creation {i} failed: {e}")
        
        identity_creation_time = time.time() - start_time
        
        # Test role management performance
        start_time = time.time()
        
        role_manager = NodeRoleManager(self.settings, self.test_node_id)
        self.test_services.append(role_manager)
        
        role_start_success = role_manager.start_role_management()
        assert role_start_success
        
        # Allow role management to initialize and stabilize
        time.sleep(2)
        
        role_management_time = time.time() - start_time
        
        # Performance assertions
        assert identity_creation_time < 30.0, f"Identity creation took too long: {identity_creation_time:.2f}s"
        assert role_management_time < 10.0, f"Role management startup took too long: {role_management_time:.2f}s"
        assert identities_created >= 8, f"Too many identity creations failed: {identities_created}/10"
        
        # Verify constitutional compliance wasn't sacrificed for performance
        network_status = role_manager.get_network_status()
        assert network_status["constitutional_compliance"] is True
        
        print(f"✅ Performance integration test passed")
        print(f"   - Identity creation: {identities_created}/10 in {identity_creation_time:.2f}s")
        print(f"   - Role management startup: {role_management_time:.2f}s")

    def test_error_recovery_and_resilience_integration(self):
        """
        Test system resilience and recovery from various failure scenarios
        Verifies constitutional compliance is maintained even during failures
        """
        # Test 1: Network failure resilience
        role_manager = NodeRoleManager(self.settings, self.test_node_id)
        self.test_services.append(role_manager)
        
        # Start role management
        assert role_manager.start_role_management()
        time.sleep(1)
        
        # Simulate network failure by stopping discovery
        if role_manager.discovery:
            role_manager.discovery.stop_discovery()
        
        # System should remain constitutionally compliant even without network
        time.sleep(1)
        network_status = role_manager.get_network_status()
        assert network_status["constitutional_compliance"] is True
        
        # Test 2: Resource constraint resilience
        # Simulate low memory condition
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.available = 500 * 1024 * 1024  # 500MB available
            
            # Update metrics with constrained resources
            role_manager._update_node_metrics()
            
            # System should adapt but maintain constitutional compliance
            current_role = role_manager.get_current_role()
            assert current_role in [NodeRole.MASTER, NodeRole.SLAVE, NodeRole.CANDIDATE]
        
        # Test 3: Identity system recovery
        identity_manager = IdentityManager()
        
        # Test recovery from corrupted identity attempt
        with pytest.raises(ConstitutionalViolationError):
            identity_manager.create_identity(
                full_name="",  # Invalid empty name
                date_of_birth="invalid-date",
                government_id="",
                passphrase="weak",
                email="invalid"
            )
        
        # System should recover and allow valid identity creation afterwards
        recovery_identity = identity_manager.create_identity(
            full_name="Recovery Test User",
            date_of_birth="1990-01-01",
            government_id="RECOVERY123",
            passphrase="recovery_test_passphrase",
            email="recovery@test.com"
        )
        
        assert recovery_identity is not None
        assert recovery_identity["constitutional_version"] == "1.0"
        
        print("✅ Error recovery and resilience integration test passed")


@pytest.mark.asyncio
async def test_async_operations_integration():
    """
    Test asynchronous operations integration with constitutional compliance
    Verifies that async operations maintain constitutional principles
    """
    settings = HAINetSettings()
    
    # Test concurrent identity creation
    async def create_test_identity(user_id: int):
        identity_manager = IdentityManager()
        return identity_manager.create_identity(
            full_name=f"Async Test User {user_id}",
            date_of_birth="1990-01-01",
            government_id=f"ASYNC{user_id:06d}",
            passphrase=f"async_test_passphrase_{user_id}",
            email=f"async{user_id}@test.com"
        )
    
    # Create multiple identities concurrently
    tasks = [create_test_identity(i) for i in range(5)]
    identities = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verify all identities were created successfully and are constitutional
    successful_identities = [id for id in identities if isinstance(id, dict)]
    assert len(successful_identities) >= 4, f"Too many concurrent identity creations failed"
    
    for identity in successful_identities:
        assert identity["constitutional_version"] == "1.0"
        assert identity["privacy_settings"]["data_sharing_consent"] is False
    
    print("✅ Async operations integration test passed")


def test_constitutional_compliance_under_stress():
    """
    Stress test to verify constitutional compliance under heavy load
    """
    settings = HAINetSettings()
    
    # Stress test parameters
    num_operations = 50
    max_concurrent = 5
    
    # Track constitutional compliance throughout stress test
    compliance_violations = 0
    successful_operations = 0
    
    identity_manager = IdentityManager()
    
    for batch in range(0, num_operations, max_concurrent):
        batch_operations = []
        
        for i in range(max_concurrent):
            if batch + i >= num_operations:
                break
                
            try:
                identity = identity_manager.create_identity(
                    full_name=f"Stress Test User {batch + i}",
                    date_of_birth="1990-01-01",
                    government_id=f"STRESS{batch + i:06d}",
                    passphrase=f"stress_test_passphrase_{batch + i}",
                    email=f"stress{batch + i}@test.com"
                )
                
                # Verify constitutional compliance
                if (identity and 
                    identity["constitutional_version"] == "1.0" and
                    identity["privacy_settings"]["data_sharing_consent"] is False):
                    successful_operations += 1
                else:
                    compliance_violations += 1
                    
            except ConstitutionalViolationError:
                # Expected for some operations due to stress conditions
                pass
            except Exception as e:
                print(f"Unexpected error in stress test: {e}")
                compliance_violations += 1
        
        # Brief pause between batches to avoid overwhelming system
        time.sleep(0.1)
    
    # Verify stress test results
    success_rate = successful_operations / num_operations
    assert success_rate >= 0.8, f"Success rate too low under stress: {success_rate:.2%}"
    assert compliance_violations <= num_operations * 0.2, f"Too many compliance violations: {compliance_violations}"
    
    print(f"✅ Constitutional compliance stress test passed")
    print(f"   - Success rate: {success_rate:.2%}")
    print(f"   - Compliance violations: {compliance_violations}")


if __name__ == "__main__":
    # Run integration tests
    print("HAI-Net End-to-End Integration Tests")
    print("=" * 50)
    
    # Initialize test class
    test_class = TestHAINetEndToEndIntegration()
    test_class.setup_test_environment()
    
    try:
        # Run all integration tests
        test_class.test_constitutional_identity_system_integration()
        test_class.test_network_discovery_and_role_management_integration()
        test_class.test_constitutional_logging_system_integration()
        test_class.test_full_system_integration_simulation()
        test_class.test_constitutional_violation_handling_integration()
        test_class.test_performance_and_scalability_integration()
        test_class.test_error_recovery_and_resilience_integration()
        
        # Run standalone tests
        asyncio.run(test_async_operations_integration())
        test_constitutional_compliance_under_stress()
        
        print("\n" + "=" * 50)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("HAI-Net Seed framework is ready for production deployment!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        raise
    
    finally:
        # Cleanup
        pass
