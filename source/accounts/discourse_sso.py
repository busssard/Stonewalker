"""
Discourse SSO (DiscourseConnect) helper functions.

This module implements the DiscourseConnect SSO protocol, which allows users
to authenticate on Discourse using their Django credentials.

Protocol documentation: https://meta.discourse.org/t/discourseconnect-official-single-sign-on-for-discourse-sso/13045
"""
import base64
import hashlib
import hmac
from urllib.parse import parse_qs, urlencode


def validate_discourse_payload(payload: str, signature: str, secret: str) -> bool:
    """
    Validate the SSO payload signature from Discourse.

    Args:
        payload: Base64-encoded payload from Discourse
        signature: HMAC-SHA256 signature (hex encoded)
        secret: Shared SSO secret

    Returns:
        True if the signature is valid, False otherwise
    """
    if not payload or not signature or not secret:
        return False

    try:
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, signature)
    except Exception:
        return False


def parse_discourse_payload(payload: str) -> str:
    """
    Parse the SSO payload and extract the nonce.

    Args:
        payload: Base64-encoded payload from Discourse

    Returns:
        The nonce value from the payload

    Raises:
        ValueError: If payload is invalid or nonce is missing
    """
    try:
        decoded = base64.b64decode(payload).decode('utf-8')
        params = parse_qs(decoded)
        nonce = params.get('nonce', [None])[0]
        if not nonce:
            raise ValueError("Nonce not found in payload")
        return nonce
    except Exception as e:
        raise ValueError(f"Invalid payload: {e}")


def generate_discourse_payload(user, nonce: str, secret: str, request=None) -> str:
    """
    Generate a signed SSO response payload to send back to Discourse.

    Args:
        user: Django User object
        nonce: The nonce from the original request
        secret: Shared SSO secret
        request: Optional Django request object (for building avatar URL)

    Returns:
        URL-encoded query string with sso and sig parameters
    """
    # Build user data payload
    user_data = {
        'nonce': nonce,
        'external_id': str(user.id),
        'email': user.email,
        'username': user.username,
        'name': user.get_full_name() or user.username,
    }

    # Add avatar URL if user has a profile picture
    if hasattr(user, 'profile') and user.profile.profile_picture:
        if request:
            avatar_url = request.build_absolute_uri(user.profile.profile_picture.url)
            user_data['avatar_url'] = avatar_url

    # Encode payload
    payload_str = urlencode(user_data)
    payload_b64 = base64.b64encode(payload_str.encode('utf-8')).decode('utf-8')

    # Sign payload
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return urlencode({'sso': payload_b64, 'sig': signature})
