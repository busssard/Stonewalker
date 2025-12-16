"""
Custom email backends for Django.
"""
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class MailjetEmailBackend(BaseEmailBackend):
    """
    Custom email backend for Mailjet using their REST API.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        try:
            from mailjet_rest import Client
            import os
            
            self.api_key = os.environ.get('MJ_APIKEY_PUBLIC')
            self.api_secret = os.environ.get('MJ_APIKEY_PRIVATE')
            
            if not self.api_key or not self.api_secret:
                raise ValueError(
                    "MJ_APIKEY_PUBLIC and MJ_APIKEY_PRIVATE environment variables "
                    "must be set for Mailjet email backend."
                )
            
            self.mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
        except ImportError:
            if not fail_silently:
                raise ImportError(
                    "mailjet_rest library is required. Install it with: pip install mailjet-rest"
                )
            self.mailjet = None
        except Exception as e:
            if not fail_silently:
                raise
            logger.error(f"Failed to initialize Mailjet backend: {str(e)}")
            self.mailjet = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of messages sent.
        """
        if not self.mailjet:
            return 0
        
        if not email_messages:
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                # Extract email data
                from_email = message.from_email
                to_emails = message.to
                subject = message.subject
                
                # Get text and HTML content
                text_content = None
                html_content = None
                
                if hasattr(message, 'body'):
                    text_content = message.body
                
                # Check for alternatives (HTML content)
                if hasattr(message, 'alternatives') and message.alternatives:
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            html_content = content
                            break
                
                # Prepare Mailjet message format
                mailjet_data = {
                    'Messages': [
                        {
                            'From': {
                                'Email': from_email,
                                'Name': getattr(settings, 'DEFAULT_FROM_EMAIL_NAME', 'Me')
                            },
                            'To': [
                                {
                                    'Email': to_email,
                                    'Name': to_email.split('@')[0]  # Use email prefix as name
                                }
                                for to_email in to_emails
                            ],
                            'Subject': subject,
                        }
                    ]
                }
                
                # Add text and HTML parts
                if text_content:
                    mailjet_data['Messages'][0]['TextPart'] = text_content
                if html_content:
                    mailjet_data['Messages'][0]['HTMLPart'] = html_content
                elif text_content:
                    # If only text and no HTML, use text for HTML part as well
                    mailjet_data['Messages'][0]['HTMLPart'] = text_content
                
                # Send via Mailjet API
                result = self.mailjet.send.create(data=mailjet_data)
                
                # Check response
                if result.status_code == 200:
                    response_data = result.json()
                    if response_data.get('Messages'):
                        message_status = response_data['Messages'][0].get('Status')
                        if message_status == 'success':
                            num_sent += 1
                            logger.info(f"Successfully sent email to {', '.join(to_emails)}")
                        else:
                            logger.error(f"Mailjet returned non-success status: {message_status}")
                            if not self.fail_silently:
                                raise Exception(f"Mailjet API error: {message_status}")
                    else:
                        logger.error(f"Unexpected Mailjet response: {response_data}")
                        if not self.fail_silently:
                            raise Exception(f"Unexpected Mailjet response: {response_data}")
                else:
                    error_msg = f"Mailjet API returned status code {result.status_code}"
                    logger.error(error_msg)
                    if not self.fail_silently:
                        raise Exception(error_msg)
                        
            except Exception as e:
                logger.error(f"Failed to send email via Mailjet: {str(e)}")
                if not self.fail_silently:
                    raise
        
        return num_sent

