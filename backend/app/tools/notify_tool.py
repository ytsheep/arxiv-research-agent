"""Notify tool: send email and Feishu notifications."""

import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logging import logger


class NotifyTool:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def send_email(self, to: list[str], subject: str, content_markdown: str) -> dict:
        """Send email via SMTP."""
        if not settings.smtp_host:
            return {"success": False, "sent": False, "error": "SMTP not configured"}

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_from or settings.smtp_user
            msg["To"] = ", ".join(to)

            # Plain text fallback
            plain = content_markdown.replace("#", "").replace("*", "").replace("`", "")
            msg.attach(MIMEText(plain, "plain", "utf-8"))

            # HTML version
            html_content = self._markdown_to_html(content_markdown)
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            port = int(settings.smtp_port) if settings.smtp_port else 587
            with smtplib.SMTP(settings.smtp_host, port, timeout=15) as server:
                server.starttls()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}: {subject}")
            return {"success": True, "sent": True, "error": None}

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return {"success": False, "sent": False, "error": str(e)}

    async def send_feishu(self, webhook_ref: str, title: str, content_markdown: str) -> dict:
        """Send Feishu bot message via webhook."""
        webhook_url = webhook_ref or settings.feishu_default_webhook
        if not webhook_url:
            return {"success": False, "sent": False, "error": "Feishu webhook not configured"}

        try:
            # Build Feishu interactive card
            card = self._build_feishu_card(title, content_markdown)
            payload = {
                "msg_type": "interactive",
                "card": card,
            }

            client = await self._get_client()
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                logger.info(f"Feishu message sent: {title}")
                return {"success": True, "sent": True, "error": None}
            else:
                return {"success": False, "sent": False, "error": result.get("msg", str(result))}

        except Exception as e:
            logger.error(f"Feishu send failed: {e}")
            return {"success": False, "sent": False, "error": str(e)}

    def _markdown_to_html(self, md: str) -> str:
        """Simple markdown to HTML conversion for email."""
        import re
        lines = md.split("\n")
        html = ['<html><body style="font-family: sans-serif; max-width: 700px;">']
        in_list = False

        for line in lines:
            if line.startswith("### "):
                if in_list:
                    html.append("</ul>")
                    in_list = False
                html.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith("## "):
                if in_list:
                    html.append("</ul>")
                    in_list = False
                html.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith("# "):
                html.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith("- "):
                if not in_list:
                    html.append("<ul>")
                    in_list = True
                html.append(f"<li>{line[2:]}</li>")
            elif line.startswith("**") and "**" in line[2:]:
                html.append(f"<p><strong>{line.strip('*')}</strong></p>")
            elif line.strip():
                if in_list:
                    html.append("</ul>")
                    in_list = False
                # Make arxiv IDs clickable
                line = re.sub(r'(\d{4}\.\d{4,})', r'<a href="https://arxiv.org/abs/\1">\1</a>', line)
                html.append(f"<p>{line}</p>")
            else:
                if in_list:
                    html.append("</ul>")
                    in_list = False

        if in_list:
            html.append("</ul>")
        html.append("</body></html>")
        return "\n".join(html)

    def _build_feishu_card(self, title: str, content: str) -> dict:
        """Build a Feishu message card."""
        # Truncate content for Feishu card
        body_text = content[:3000]
        if len(content) > 3000:
            body_text += "\n\n...(内容过长已截断)"

        return {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": body_text,
                }
            ],
        }

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
