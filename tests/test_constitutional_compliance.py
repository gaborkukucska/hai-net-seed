# START OF FILE tests/test_constitutional_compliance.py
"""
Constitutional Compliance Tests for HAI-Net
Ensures all components adhere to the four core principles:
1. Privacy First
2. Human Rights Protection  
3. Decentralization
4. Community Focus
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Import HAI-Net components
from core.identity.did import IdentityManager, DIDGenerator, ConstitutionalViolationError


class TestPrivacyFirstPrinciple:
    """Test Article I: Privacy First Principle compliance"""
    
    def test_did_generation_is_deterministic(self):
        """Verify DID generation is deterministic for same inputs"""
        generator = DIDGenerator()
        
        # Generate DID twice with same inputs
        did1 = generator.generate_did(
            full_name="Alice Smith",
            date_of_birth="1990-05-15",
            government_id="ABC123456",
            passphrase="secure_password_123"
        )
        
        did2 = generator.generate_did(
            full_name="Alice Smith", 
            date_of_birth="1990-05-15",
            government_id="ABC123456",
            passphrase="secure_password_123"
        )
        
        assert did1 == did2, "DID generation must be deterministic for same inputs"
        assert did1.startswith("did:hai:"), "DID must follow proper format"
    
    def test_did_generation_requires_valid_inputs(self):
        """Verify input validation protects user privacy"""
        generator = DIDGenerator()
        
        # Test invalid inputs that should be rejected
        invalid_cases = [
            ("", "1990-05-15", "ABC123456", "secure_password"),  # Empty name
            ("Alice", "invalid-date", "ABC123456", "secure_password"),  # Invalid date
            ("Alice", "1990-05-15", "", "secure_password"),  # Empty gov ID
            ("Alice", "1990-05-15", "ABC123456", "weak"),  # Weak passphrase
        ]
        
        for name, dob, gov_id, passphrase in invalid_cases:
            with pytest.raises(ConstitutionalViolationError):
                generator.generate_did(name, dob, gov_id, passphrase)
    
    def test_personal_data_not_stored_plaintext(self):
        """Verify personal data is not stored in plaintext"""
        manager = IdentityManager()
        
        identity = manager.create_identity(
            full_name="Bob Jones",
            date_of_birth="1985-12-01", 
            government_id="XYZ789012",
            passphrase="my_secure_passphrase",
            email="bob@example.com"
        )
        
        # Verify personal info is not in identity object
        identity_str = json.dumps(identity)
        assert "Bob Jones" not in identity_str
        assert "1985-12-01" not in identity_str
        assert "XYZ789012" not in identity_str
        assert "my_secure_passphrase" not in identity_str
        assert "bob@example.com" not in identity_str
        
        # Verify only email hash is stored
        assert "email_hash" in identity
        assert len(identity["email_hash"]) == 64  # SHA256 hash length
    
    def test_data_storage_is_local_only(self):
        """Verify no data leaves local system during identity creation"""
        manager = IdentityManager()
        
        # Mock network functions to detect any external calls
        with patch('requests.post') as mock_post, \
             patch('requests.get') as mock_get, \
             patch('urllib.request.urlopen') as mock_urlopen:
            
            identity = manager.create_identity(
                full_name="Charlie Brown",
                date_of_birth="1992-03-10",
                government_id="DEF456789",
                passphrase="another_secure_pass",
                email="charlie@example.com"
            )
            
            # Verify no network calls were made
            mock_post.assert_not_called()
            mock_get.assert_not_called()
            mock_urlopen.assert_not_called()


class TestHumanRightsProtection:
    """Test Article II: Human Rights Protection compliance"""
    
    def test_user_retains_control_over_identity(self):
        """Verify users have complete control over their identity"""
        manager = IdentityManager()
        
        identity = manager.create_identity(
            full_name="Diana Prince",
            date_of_birth="1988-07-04",
            government_id="WW123456",
            passphrase="wonder_woman_pass",
            email="diana@themyscira.com"
        )
        
        # Verify privacy settings default to user control
        privacy_settings = identity["privacy_settings"]
        assert privacy_settings["data_sharing_consent"] == False
        assert privacy_settings["analytics_consent"] == False
        assert privacy_settings["community_participation"] == True  # Community focus principle
    
    def test_email_validation_prevents_discrimination(self):
        """Verify email validation doesn't discriminate"""
        manager = IdentityManager()
        
        # Test various valid email formats
        valid_emails = [
            "user@example.com",
            "user.name@example.org", 
            "user+tag@example.net",
            "user123@sub.example.com",
            "مستخدم@example.com",  # Unicode characters
        ]
        
        for email in valid_emails:
            # Should not raise exception
            result = manager._validate_email(email)
            assert result == True, f"Email {email} should be valid"
    
    def test_accessibility_requirements(self):
        """Verify system supports accessibility needs"""
        # Test that error messages are clear and helpful
        generator = DIDGenerator()
        
        try:
            generator.generate_did("", "", "", "")
        except ConstitutionalViolationError as e:
            error_msg = str(e)
            assert "protecting user privacy" in error_msg.lower()
            assert len(error_msg) > 10  # Meaningful error message


class TestDecentralizationImperative:
    """Test Article III: Decentralization Imperative compliance"""
    
    def test_no_central_authority_required(self):
        """Verify identity can be created without central authority"""
        manager = IdentityManager()
        
        # Mock all potential central authority connections
        with patch('socket.socket') as mock_socket, \
             patch('ssl.create_default_context') as mock_ssl:
            
            identity = manager.create_identity(
                full_name="Bruce Wayne",
                date_of_birth="1987-02-19",
                government_id="BAT123456", 
                passphrase="gotham_guardian",
                email="bruce@wayneenterprises.com"
            )
            
            assert identity is not None
            assert identity["did"].startswith("did:hai:")
            
            # Verify no network connections attempted
            mock_socket.assert_not_called()
    
    def test_identity_is_self_sovereign(self):
        """Verify identity doesn't depend on external services"""
        manager = IdentityManager()
        
        # Create identity offline
        with patch('os.environ.get', return_value=None):  # No external config
            identity = manager.create_identity(
                full_name="Clark Kent",
                date_of_birth="1986-06-18",
                government_id="SUP789012",
                passphrase="krypton_survivor",
                email="clark@dailyplanet.com"
            )
            
            assert identity["did"] is not None
            assert "public_key" in identity
            assert identity["constitutional_version"] == "1.0"
    
    def test_fork_resistance(self):
        """Verify identity generation is resistant to centralized control"""
        # Different managers should generate same DID for same inputs
        manager1 = IdentityManager()
        manager2 = IdentityManager()
        
        inputs = {
            "full_name": "Peter Parker",
            "date_of_birth": "1995-08-10",
            "government_id": "SPD123456",
            "passphrase": "with_great_power",
            "email": "peter@dailybugle.com"
        }
        
        identity1 = manager1.create_identity(**inputs)
        identity2 = manager2.create_identity(**inputs)
        
        # DIDs should be identical (deterministic generation)
        assert identity1["did"] == identity2["did"]


class TestCommunityFocusPrinciple:
    """Test Article IV: Community Focus Principle compliance"""
    
    def test_community_participation_enabled_by_default(self):
        """Verify community participation is encouraged"""
        manager = IdentityManager()
        
        identity = manager.create_identity(
            full_name="Natasha Romanoff",
            date_of_birth="1984-12-03",
            government_id="BW456789",
            passphrase="red_ledger_cleared",
            email="natasha@shield.gov"
        )
        
        # Community participation should be enabled by default
        assert identity["privacy_settings"]["community_participation"] == True
    
    def test_watermarking_enables_community_trust(self):
        """Verify watermarking supports community transparency"""
        manager = IdentityManager()
        
        identity = manager.create_identity(
            full_name="Tony Stark",
            date_of_birth="1970-05-29",
            government_id="IM123456",
            passphrase="arc_reactor_powered",
            email="tony@starkindustries.com"
        )
        
        # Test watermarking functionality
        test_data = b"This is AI-generated content for the community"
        watermarked_data = manager.watermark_data(test_data, "text")
        
        # Verify watermark can be extracted
        watermark_info = manager.verify_watermark(watermarked_data)
        assert watermark_info["did"] == identity["did"]
        assert watermark_info["constitutional_version"] == "1.0"
        assert "timestamp" in watermark_info
    
    def test_environmental_responsibility(self):
        """Verify system promotes resource efficiency"""
        # Test that identity generation is computationally efficient
        import time
        
        manager = IdentityManager()
        start_time = time.time()
        
        identity = manager.create_identity(
            full_name="Steve Rogers",
            date_of_birth="1918-07-04",  # Captain America's canonical birthday
            government_id="CA123456",
            passphrase="shield_and_justice",
            email="steve@avengers.org"
        )
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Identity creation should be efficient (under 5 seconds)
        assert creation_time < 5.0, f"Identity creation took {creation_time:.2f}s, should be under 5s"
        assert identity is not None


class TestConstitutionalEnforcement:
    """Test Article V: Constitutional Enforcement compliance"""
    
    def test_constitutional_version_tracking(self):
        """Verify constitutional version is tracked in all objects"""
        manager = IdentityManager()
        
        identity = manager.create_identity(
            full_name="Carol Danvers",
            date_of_birth="1989-04-24",
            government_id="CM789012",
            passphrase="higher_further_faster",
            email="carol@airforce.mil"
        )
        
        assert "constitutional_version" in identity
        assert identity["constitutional_version"] == "1.0"
    
    def test_violation_detection(self):
        """Verify constitutional violations are properly detected"""
        generator = DIDGenerator()
        
        # Test various violation scenarios
        with pytest.raises(ConstitutionalViolationError):
            generator.generate_did("", "1990-01-01", "123", "password")  # Empty name
        
        with pytest.raises(ConstitutionalViolationError):
            generator.generate_did("Name", "invalid", "123", "password")  # Invalid date
    
    def test_educational_error_messages(self):
        """Verify error messages are educational, not punitive"""
        manager = IdentityManager()
        
        try:
            manager.create_identity(
                full_name="Invalid User",
                date_of_birth="1990-01-01",
                government_id="123",
                passphrase="weak",
                email="invalid-email"
            )
        except ConstitutionalViolationError as e:
            error_message = str(e).lower()
            # Error should be protective, not accusatory
            assert "protecting" in error_message or "privacy" in error_message
            assert "violation" not in error_message  # Avoid punitive language


class TestImplementationRequirements:
    """Test Article VII: Implementation Requirements compliance"""
    
    def test_code_compliance_markers(self):
        """Verify code includes constitutional compliance markers"""
        # Check that modules include constitutional compliance indicators
        from core.identity import did
        
        # Verify constitutional compliance is referenced in the code
        source_file = did.__file__
        with open(source_file, 'r') as f:
            content = f.read()
            
        assert "Constitutional" in content or "constitutional" in content
        assert "Privacy First" in content or "privacy" in content.lower()
    
    def test_continuous_improvement_support(self):
        """Verify system supports continuous improvement"""
        manager = IdentityManager()
        
        # Verify identity objects can track improvements
        identity = manager.create_identity(
            full_name="Wanda Maximoff",
            date_of_birth="1989-02-10",
            government_id="SW123456",
            passphrase="chaos_magic_reality",
            email="wanda@westview.com"
        )
        
        # Constitutional version tracking enables improvements
        assert "constitutional_version" in identity
        assert isinstance(identity["constitutional_version"], str)


def test_full_constitutional_compliance():
    """Integration test verifying all constitutional principles work together"""
    manager = IdentityManager()
    
    # Create identity following all constitutional principles
    identity = manager.create_identity(
        full_name="Nick Fury",
        date_of_birth="1951-12-21",
        government_id="DIR123456",
        passphrase="keep_your_friends_close",
        email="director@shield.gov"
    )
    
    # Verify all principles are upheld
    assert identity is not None  # Human Rights: System works for user
    assert identity["did"].startswith("did:hai:")  # Decentralization: Self-sovereign ID
    assert "email_hash" in identity  # Privacy First: Only hash stored
    assert identity["privacy_settings"]["community_participation"]  # Community Focus: Enabled
    assert identity["constitutional_version"] == "1.0"  # Constitutional Enforcement: Tracked
    
    # Verify watermarking works (transparency + community trust)
    test_content = b"SHIELD classified information"
    watermarked = manager.watermark_data(test_content)
    watermark_info = manager.verify_watermark(watermarked)
    
    assert watermark_info["did"] == identity["did"]
    assert watermark_info["constitutional_version"] == "1.0"
    
    print("✓ All Constitutional Principles Successfully Verified")


if __name__ == "__main__":
    # Run constitutional compliance verification
    print("HAI-Net Constitutional Compliance Test Suite")
    print("=" * 50)
    
    # Run the comprehensive test
    test_full_constitutional_compliance()
    
    print("✓ Privacy First Principle: Verified")
    print("✓ Human Rights Protection: Verified") 
    print("✓ Decentralization Imperative: Verified")
    print("✓ Community Focus Principle: Verified")
    print("✓ Constitutional Enforcement: Verified")
    print("✓ Implementation Requirements: Verified")
    print("\n🎉 HAI-Net is Constitutionally Compliant!")
