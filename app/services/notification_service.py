import smtplib
from email.mime.text import MIMEText
from typing import Iterable, List

import requests

from app.models import DeliveryResult, DigestResult
from app.config import Settings


class EmailNotifier:
    def __init__(self, settings: Settings):
        self.settings = settings

    def is_enabled(self) -> bool:
        required = [
            self.settings.smtp_host,
            self.settings.smtp_username,
            self.settings.smtp_password,
            self.settings.email_from,
        ]
        return all(required)

    def send(self, subject: str, body: str, to_address: str) -> None:
        if not self.is_enabled():
            raise ValueError("Email notifier is not fully configured.")

        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = self.settings.email_from
        message["To"] = to_address

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=30) as server:
            if self.settings.smtp_use_tls:
                server.starttls()
            server.login(self.settings.smtp_username, self.settings.smtp_password)
            server.sendmail(self.settings.email_from, [to_address], message.as_string())


class FeishuNotifier:
    @staticmethod
    def send(title: str, body: str, webhook_url: str) -> None:
        payload = {
            "msg_type": "text",
            "content": {
                "text": f"{title}\n\n{body}",
            },
        }
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()


class NotificationManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.email_notifier = EmailNotifier(settings)
        self.feishu_notifier = FeishuNotifier()

    def notify_digest(self, result: DigestResult, recipients: Iterable[dict]) -> List[DeliveryResult]:
        title = f"arXiv 每日精选论文 | {result.generated_at.strftime('%Y-%m-%d')}"
        deliveries: List[DeliveryResult] = []

        for recipient in recipients:
            channel = str(recipient["channel"])
            target = str(recipient["target"])
            try:
                if channel == "email":
                    self.email_notifier.send(title, result.plain_text, target)
                elif channel == "feishu":
                    self.feishu_notifier.send(title, result.plain_text, target)
                else:
                    raise ValueError(f"Unsupported channel: {channel}")
                deliveries.append(
                    DeliveryResult(channel=channel, target=target, status="success")
                )
            except Exception as exc:
                deliveries.append(
                    DeliveryResult(
                        channel=channel,
                        target=target,
                        status="failed",
                        error_message=str(exc),
                    )
                )

        return deliveries
