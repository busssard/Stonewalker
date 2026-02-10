"""
Validators for user-submitted content in StoneWalker.

Prevents contact information (emails, URLs, phone numbers) from being
embedded in stone comments and descriptions.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Email pattern: user@domain.tld
EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
)

# URL pattern: http(s):// or www. or domain.common-tld
URL_RE = re.compile(
    r'https?://|www\.|[a-zA-Z0-9.\-]+\.(com|org|net|io|co)\b'
)

# Phone pattern: optional country code, groups of digits with separators
PHONE_RE = re.compile(
    r'(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
)

CONTACT_INFO_ERROR = _(
    "Comments cannot contain contact information "
    "(emails, websites, or phone numbers)."
)


def validate_no_contact_info(text):
    """Raise ValidationError if text contains emails, URLs, or phone numbers."""
    if not text:
        return
    if EMAIL_RE.search(text):
        raise ValidationError(CONTACT_INFO_ERROR)
    if URL_RE.search(text):
        raise ValidationError(CONTACT_INFO_ERROR)
    if PHONE_RE.search(text):
        raise ValidationError(CONTACT_INFO_ERROR)
