"""
Tests for email validation and normalization (DISC-017).

Tests trial abuse prevention features:
- Email normalization (Gmail dots and plus aliases)
- Disposable email detection
"""

import pytest
from backend.utils.email import (
    normalize_email,
    is_disposable_email,
    validate_email_for_registration
)


class TestEmailNormalization:
    """Test email normalization for duplicate detection."""

    def test_normalize_gmail_dots(self):
        """Should remove dots from Gmail usernames."""
        assert normalize_email("j.ohn@gmail.com") == "john@gmail.com"
        assert normalize_email("jo.h.n@gmail.com") == "john@gmail.com"
        assert normalize_email("john.doe@gmail.com") == "johndoe@gmail.com"

    def test_normalize_gmail_plus_alias(self):
        """Should remove plus aliases from Gmail addresses."""
        assert normalize_email("john+trial@gmail.com") == "john@gmail.com"
        assert normalize_email("john+test123@gmail.com") == "john@gmail.com"
        assert normalize_email("user+anything@gmail.com") == "user@gmail.com"

    def test_normalize_gmail_combined(self):
        """Should handle both dots and plus aliases together."""
        assert normalize_email("j.ohn+trial@gmail.com") == "john@gmail.com"
        assert normalize_email("John.Doe+test@Gmail.COM") == "johndoe@gmail.com"

    def test_normalize_googlemail(self):
        """Should normalize googlemail.com to gmail.com."""
        assert normalize_email("john@googlemail.com") == "john@gmail.com"
        assert normalize_email("j.ohn+test@googlemail.com") == "john@gmail.com"

    def test_normalize_case_insensitive(self):
        """Should lowercase all emails."""
        assert normalize_email("John@Gmail.com") == "john@gmail.com"
        assert normalize_email("USER@YAHOO.COM") == "user@yahoo.com"

    def test_normalize_other_providers(self):
        """Should handle non-Gmail providers (just remove plus aliases)."""
        assert normalize_email("user+test@yahoo.com") == "user@yahoo.com"
        assert normalize_email("user+123@outlook.com") == "user@outlook.com"
        # Don't remove dots for non-Gmail
        assert normalize_email("j.ohn@yahoo.com") == "j.ohn@yahoo.com"

    def test_normalize_whitespace(self):
        """Should trim whitespace."""
        assert normalize_email("  john@gmail.com  ") == "john@gmail.com"
        assert normalize_email("\tuser@example.com\n") == "user@example.com"


class TestDisposableEmailDetection:
    """Test disposable email domain detection."""

    def test_detect_common_disposable_domains(self):
        """Should detect common disposable email domains."""
        disposable_domains = [
            "mailinator.com",
            "10minutemail.com",
            "tempmail.com",
            "guerrillamail.com",
            "throwaway.email",
            "temp-mail.org",
            "fakeinbox.com",
            "getnada.com",
            "maildrop.cc",
            "yopmail.com",
        ]
        for domain in disposable_domains:
            assert is_disposable_email(f"user@{domain}") is True

    def test_allow_legitimate_domains(self):
        """Should allow legitimate email domains."""
        legitimate_domains = [
            "gmail.com",
            "yahoo.com",
            "outlook.com",
            "hotmail.com",
            "protonmail.com",
            "icloud.com",
            "aol.com",
            "company.com",
        ]
        for domain in legitimate_domains:
            assert is_disposable_email(f"user@{domain}") is False

    def test_case_insensitive_detection(self):
        """Should detect disposable emails case-insensitively."""
        assert is_disposable_email("user@MAILINATOR.COM") is True
        assert is_disposable_email("User@TempMail.Com") is True


class TestEmailValidationForRegistration:
    """Test complete email validation for registration."""

    def test_accept_valid_emails(self):
        """Should accept valid, permanent email addresses."""
        valid_emails = [
            "john@gmail.com",
            "user@yahoo.com",
            "contractor@company.com",
            "info@business.co.uk",
        ]
        for email in valid_emails:
            is_valid, error = validate_email_for_registration(email)
            assert is_valid is True
            assert error is None

    def test_reject_disposable_emails(self):
        """Should reject disposable email addresses with friendly message."""
        disposable_emails = [
            "test@mailinator.com",
            "user@10minutemail.com",
            "fake@tempmail.com",
        ]
        for email in disposable_emails:
            is_valid, error = validate_email_for_registration(email)
            assert is_valid is False
            assert error == "Please use a permanent email address"


class TestIntegrationScenarios:
    """Test real-world abuse scenarios."""

    def test_gmail_alias_variations(self):
        """Should detect all Gmail alias variations as duplicates."""
        base_email = "john@gmail.com"
        aliases = [
            "j.ohn@gmail.com",
            "jo.hn@gmail.com",
            "john+trial@gmail.com",
            "john+trial2@gmail.com",
            "j.ohn+test@gmail.com",
            "John@Gmail.com",
            "john@googlemail.com",
        ]

        normalized_base = normalize_email(base_email)
        for alias in aliases:
            assert normalize_email(alias) == normalized_base

    def test_cannot_bypass_with_disposable_email(self):
        """Should block disposable emails even with normalization tricks."""
        tricky_disposables = [
            "user+bypass@mailinator.com",
            "User@MAILINATOR.COM",
            "  test@tempmail.com  ",
        ]
        for email in tricky_disposables:
            is_valid, error = validate_email_for_registration(email)
            assert is_valid is False
            assert "permanent email" in error.lower()
