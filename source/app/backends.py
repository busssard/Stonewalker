"""
Custom email backends for Django.
"""
import json
import logging
import urllib.request
import urllib.error
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)

MAILEROO_API_URL = 'https://smtp.maileroo.com/api/v2/emails'


class MailerooEmailBackend(BaseEmailBackend):
    """
    Custom email backend for Maileroo using their REST API (v2).

    Requires the MAILEROO_API_KEY environment variable to be set.
    Uses stdlib urllib — no third-party HTTP library needed.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        import os

        self.api_key = os.environ.get('MAILEROO_API_KEY')
        if not self.api_key:
            msg = "MAILEROO_API_KEY environment variable must be set for the Maileroo email backend."
            if not fail_silently:
                raise ValueError(msg)
            logger.error(msg)

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of messages sent.
        """
        if not self.api_key:
            return 0

        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                # force_str resolves Django's lazy translation proxies
                # so json.dumps doesn't choke on them
                from_email = force_str(message.from_email)
                to_emails = [force_str(addr) for addr in message.to]
                subject = force_str(message.subject)

                # Get text and HTML content
                text_content = force_str(message.body) if message.body else None
                html_content = None

                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            html_content = force_str(content)
                            break

                # If only text and no HTML, use text for HTML as well
                if not html_content and text_content:
                    html_content = text_content

                # Build Maileroo payload
                payload = {
                    'from': {
                        'address': from_email,
                        'display_name': force_str(getattr(settings, 'DEFAULT_FROM_EMAIL_NAME', 'StoneWalker')),
                    },
                    'to': [
                        {'address': addr}
                        for addr in to_emails
                    ],
                    'subject': subject,
                }

                if html_content:
                    payload['html'] = html_content
                if text_content:
                    payload['plain'] = text_content

                # CC / BCC
                if message.cc:
                    payload['cc'] = [{'address': addr} for addr in message.cc]
                if message.bcc:
                    payload['bcc'] = [{'address': addr} for addr in message.bcc]
                if message.reply_to:
                    payload['reply_to'] = [{'address': addr} for addr in message.reply_to]

                # Send via Maileroo API
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    MAILEROO_API_URL,
                    data=data,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Api-Key': self.api_key,
                    },
                    method='POST',
                )

                with urllib.request.urlopen(req) as resp:
                    body = json.loads(resp.read().decode('utf-8'))
                    if body.get('success'):
                        num_sent += 1
                        logger.info(f"Successfully sent email to {', '.join(to_emails)}")
                    else:
                        error_msg = body.get('message', 'Unknown error')
                        logger.error(f"Maileroo API error: {error_msg}")
                        if not self.fail_silently:
                            raise Exception(f"Maileroo API error: {error_msg}")

            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8', errors='replace')
                logger.error(f"Maileroo HTTP {e.code}: {error_body}")
                if not self.fail_silently:
                    raise
            except Exception as e:
                logger.error(f"Failed to send email via Maileroo: {str(e)}")
                if not self.fail_silently:
                    raise

        return num_sent
