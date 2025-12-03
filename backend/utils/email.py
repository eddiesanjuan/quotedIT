"""
Email validation utilities for trial abuse prevention (DISC-017).

Provides:
- Email normalization (strips Gmail dots and plus aliases)
- Disposable email domain detection
"""

from typing import Optional


# Known disposable email domains (DISC-017)
DISPOSABLE_EMAIL_DOMAINS = {
    'mailinator.com', '10minutemail.com', 'tempmail.com', 'guerrillamail.com',
    'throwaway.email', 'temp-mail.org', 'fakeinbox.com', 'getnada.com',
    'maildrop.cc', 'yopmail.com', 'trashmail.com', 'sharklasers.com',
    'discard.email', 'mailnesia.com', 'tempr.email', 'emailondeck.com',
    'mintemail.com', 'mytemp.email', 'temp-mail.io', 'burnermail.io',
    'spamgourmet.com', 'mailcatch.com', 'guerillamail.org', 'guerillamail.net',
    'guerillamail.biz', 'guerillamail.de', 'spam4.me', 'grr.la',
}


def normalize_email(email: str) -> str:
    """
    Normalize email address for duplicate detection.

    Gmail-specific normalizations:
    - Remove dots from username (j.ohn@gmail.com → john@gmail.com)
    - Remove plus aliases (john+trial@gmail.com → john@gmail.com)

    Other providers:
    - Lowercase entire email

    Args:
        email: Email address to normalize

    Returns:
        Normalized email address

    Examples:
        >>> normalize_email("John.Doe+trial@gmail.com")
        'johndoe@gmail.com'
        >>> normalize_email("User+123@Gmail.COM")
        'user@gmail.com'
        >>> normalize_email("test@yahoo.com")
        'test@yahoo.com'
    """
    email = email.lower().strip()

    # Split into username and domain
    if '@' not in email:
        return email

    username, domain = email.split('@', 1)

    # Gmail-specific normalization
    if domain in ['gmail.com', 'googlemail.com']:
        # Remove dots from username
        username = username.replace('.', '')
        # Remove plus aliases
        username = username.split('+')[0]
        # Normalize googlemail.com to gmail.com
        domain = 'gmail.com'
    else:
        # For other providers, just remove plus aliases
        username = username.split('+')[0]

    return f"{username}@{domain}"


def is_disposable_email(email: str) -> bool:
    """
    Check if email is from a known disposable email provider.

    Args:
        email: Email address to check

    Returns:
        True if email is from a disposable provider, False otherwise

    Examples:
        >>> is_disposable_email("user@mailinator.com")
        True
        >>> is_disposable_email("user@gmail.com")
        False
    """
    email = email.lower().strip()

    if '@' not in email:
        return False

    domain = email.split('@', 1)[1]
    return domain in DISPOSABLE_EMAIL_DOMAINS


def validate_email_for_registration(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email for registration, checking disposable providers.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid

    Examples:
        >>> validate_email_for_registration("user@gmail.com")
        (True, None)
        >>> validate_email_for_registration("user@mailinator.com")
        (False, 'Please use a permanent email address')
    """
    if is_disposable_email(email):
        return False, "Please use a permanent email address"

    return True, None
