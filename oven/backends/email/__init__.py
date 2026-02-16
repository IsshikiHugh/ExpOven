from typing import Dict
from datetime import datetime

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from oven.backends.api import NotifierBackendBase, RespStatus
from .info import EmailExpInfo, EmailLogInfo


class EmailBackend(NotifierBackendBase):
    def __init__(self, cfg: Dict):
        # Validate the configuration.
        assert (
            'smtp_server' in cfg and '<?>' not in cfg['smtp_server']
        ), 'Please ensure the validity of "email.smtp_server" field in the configuration file!'
        assert 'smtp_port' in cfg and isinstance(
            cfg['smtp_port'], int
        ), 'Please ensure the validity of "email.smtp_port" field in the configuration file!'
        assert (
            'sender_email' in cfg and '<?>' not in cfg['sender_email']
        ), 'Please ensure the validity of "email.sender_email" field in the configuration file!'
        assert (
            'sender_pwd' in cfg and '<?>' not in cfg['sender_pwd']
        ), 'Please ensure the validity of "email.sender_pwd" field in the configuration file!'
        assert (
            'receiver_email' in cfg and '<?>' not in cfg['receiver_email']
        ), 'Please ensure the validity of "email.receiver_email" field in the configuration file!'

        # Setup.
        self.cfg = cfg
        self.smtp_server = cfg['smtp_server']
        self.smtp_port = cfg['smtp_port']
        self.sender_email = cfg['sender_email']
        self.sender_pwd = cfg['sender_pwd']
        self.receiver_email = cfg['receiver_email']

    def get_meta(self) -> Dict:
        """Generate meta information for information object."""
        return {
            'host': self.cfg.get('host', None),
            'backend': 'EmailBackend',
        }

    def notify(self, info: EmailExpInfo):
        """Sending email to notify."""

        # 1. Prepare data dict.
        timestamp = int(datetime.now().timestamp())

        formatted_data = {
            'timestamp': timestamp,
            'msg_type': 'mail',
            'card': info.format_information(),
        }
        # mail config
        smtp_server = self.cfg['smtp_server']
        smtp_port = self.cfg['smtp_port']
        sender_email = self.cfg['sender_email']
        sender_password = self.cfg['sender_pwd']
        receiver_email = self.cfg['receiver_email']

        subject = formatted_data['card']['subject']
        content = formatted_data['card']['content']

        # Construct message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach content
        msg.attach(MIMEText(content, 'html'))
        has_err, err_msg = False, ''
        try:
            # Connect to the SMTP server.
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # TLS encryption
            server.login(sender_email, sender_password)  # login
            # Sending
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
        except Exception as e:
            has_err = True
            err_msg = f'Cannot send email: {e}'

        # 3. Return response dict.
        resp_status = RespStatus(has_err=has_err, err_msg=err_msg)
        return resp_status
