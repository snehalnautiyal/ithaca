"""Email service: IMAP fetch + SMTP send + AI triage."""
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.header import decode_header
from dataclasses import dataclass
from typing import Optional

from src.llm_core.settings import load_settings


@dataclass
class EmailAccount:
    name: str
    imap_host: str
    imap_port: int
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    use_ssl: bool = True


@dataclass
class EmailMessage:
    uid: str
    subject: str
    sender: str
    date: str
    snippet: str
    body: str = ""
    tags: list[str] = None
    urgency: str = "normal"  # low, normal, high, urgent
    summary: str = ""


def get_email_accounts() -> list[EmailAccount]:
    """Load email accounts from settings."""
    settings = load_settings()
    accounts = settings.get("email_accounts", [])
    return [EmailAccount(**a) for a in accounts]


def fetch_inbox(account: EmailAccount, limit: int = 20) -> list[EmailMessage]:
    """Fetch recent emails via IMAP."""
    messages = []
    try:
        if account.use_ssl:
            mail = imaplib.IMAP4_SSL(account.imap_host, account.imap_port)
        else:
            mail = imaplib.IMAP4(account.imap_host, account.imap_port)

        mail.login(account.username, account.password)
        mail.select("INBOX")

        _, data = mail.search(None, "ALL")
        uids = data[0].split()[-limit:]

        for uid in reversed(uids):
            _, msg_data = mail.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            subject = _decode_header(msg["Subject"] or "")
            sender = _decode_header(msg["From"] or "")
            date = msg["Date"] or ""

            body = _get_body(msg)
            snippet = body[:200] if body else ""

            messages.append(EmailMessage(
                uid=uid.decode(), subject=subject, sender=sender,
                date=date, snippet=snippet, body=body,
            ))

        mail.logout()
    except Exception as e:
        pass  # graceful — no crash if IMAP fails
    return messages


def send_email(account: EmailAccount, to: str, subject: str, body: str) -> bool:
    """Send email via SMTP."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = account.username
        msg["To"] = to

        if account.use_ssl:
            server = smtplib.SMTP_SSL(account.smtp_host, account.smtp_port)
        else:
            server = smtplib.SMTP(account.smtp_host, account.smtp_port)
            server.starttls()

        server.login(account.username, account.password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        return False


async def ai_triage(messages: list[EmailMessage]) -> list[EmailMessage]:
    """Use LLM to add summary, tags, and urgency to emails."""
    from src.llm_core.provider import get_provider
    provider = get_provider()

    for msg in messages[:10]:  # limit to 10 for speed
        prompt = f"""Analyze this email and return JSON:
{{"summary": "one-line summary", "tags": ["tag1", "tag2"], "urgency": "low|normal|high|urgent"}}

From: {msg.sender}
Subject: {msg.subject}
Body: {msg.body[:500]}"""

        try:
            response = ""
            async for token in provider.stream_chat([
                {"role": "system", "content": "Return only valid JSON. No explanation."},
                {"role": "user", "content": prompt},
            ]):
                response += token

            import json
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1:
                data = json.loads(response[start:end])
                msg.summary = data.get("summary", "")
                msg.tags = data.get("tags", [])
                msg.urgency = data.get("urgency", "normal")
        except Exception:
            pass
    return messages


def _decode_header(value: str) -> str:
    parts = decode_header(value)
    result = []
    for text, charset in parts:
        if isinstance(text, bytes):
            result.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(text)
    return " ".join(result)


def _get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="replace")[:3000]
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="replace")[:3000]
    return ""
