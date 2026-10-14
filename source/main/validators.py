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


# Stone names end up in URLs (/stone/<name>/edit/) and QR file paths, so only
# URL- and filename-safe characters are allowed.
STONE_NAME_MAX_LENGTH = 10
STONE_NAME_RE = re.compile(r'^[A-Za-z0-9_-]{1,%d}$' % STONE_NAME_MAX_LENGTH)


def validate_stone_name(name):
    """Raise ValidationError if name is not a valid stone name.

    The error's ``code`` ('empty', 'too_long', 'whitespace', 'invalid_chars')
    is a stable reason for API callers. Uniqueness is not checked here.
    """
    if not name:
        raise ValidationError(_('Please enter a name for your stone.'), code='empty')
    if re.search(r'\s', name):
        raise ValidationError(_('Stone name cannot contain spaces.'), code='whitespace')
    if len(name) > STONE_NAME_MAX_LENGTH:
        raise ValidationError(_('Stone name must be 10 characters or less.'), code='too_long')
    if not STONE_NAME_RE.match(name):
        raise ValidationError(
            _('Stone name can only contain letters, numbers, hyphens and underscores.'),
            code='invalid_chars',
        )
