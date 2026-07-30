import base64
import os
import urllib.parse
import urllib.request
import uuid
from typing import Any

from shared.domain.entities import (
    Issue,
    IssueStatus,
    Priority,
    Recommendation,
    RecommendationStatus,
)
from shared.domain.repositories.email import EmailRepository
from shared.domain.repositories.issue import IssueRepository
from shared.domain.repositories.notification import NotificationRepository
from shared.domain.repositories.recommendation import RecommendationRepository


def _get_notification_logger() -> Any:
    try:
        from helix_platform.logging import get_logger

        return get_logger("notifications")
    except Exception:
        import logging

        return logging.getLogger("notifications")


class SQLAlchemyIssueRepository(IssueRepository):
    """SQLAlchemy Implementation of Issue Repository."""

    def __init__(self, db_session: Any) -> None:
        self.db = db_session

    def save(self, issue: Issue) -> None:
        from services.governance.infrastructure.models import IssueModel

        db_issue = IssueModel(
            id=str(issue.id),
            citizen_id=str(issue.citizen_id),
            title=issue.title,
            description=issue.description,
            category=issue.category,
            latitude=issue.location.latitude,
            longitude=issue.location.longitude,
            status=issue.status.name,
            priority=issue.priority.name,
            created_at=issue.created_at,
        )
        self.db.merge(db_issue)
        self.db.commit()

    def get_by_id(self, issue_id: uuid.UUID) -> Issue | None:
        from services.governance.infrastructure.models import IssueModel

        db_issue = (
            self.db.query(IssueModel).filter(IssueModel.id == str(issue_id)).first()
        )
        if not db_issue:
            return None

        from shared.domain.value_objects.location import Location

        return Issue(
            id=uuid.UUID(db_issue.id),
            citizen_id=uuid.UUID(db_issue.citizen_id),
            title=db_issue.title,
            description=db_issue.description,
            category=db_issue.category,
            location=Location(latitude=db_issue.latitude, longitude=db_issue.longitude),
            status=IssueStatus[db_issue.status],
            priority=Priority[db_issue.priority],
            created_at=db_issue.created_at,
        )

    def list_pending() -> list[Issue]:
        return []


class SQLAlchemyRecommendationRepository(RecommendationRepository):
    """SQLAlchemy Implementation of Recommendation Repository."""

    def __init__(self, db_session: Any) -> None:
        self.db = db_session

    def save(self, recommendation: Recommendation) -> None:
        from services.governance.infrastructure.models import RecommendationModel

        db_rec = RecommendationModel(
            id=str(recommendation.id),
            issue_id=str(recommendation.issue_id),
            rationale=recommendation.content,
            status=recommendation.status.name,
        )
        self.db.merge(db_rec)
        self.db.commit()

    def get_by_id(self, recommendation_id: uuid.UUID) -> Recommendation | None:
        from services.governance.infrastructure.models import RecommendationModel

        db_rec = (
            self.db.query(RecommendationModel)
            .filter(RecommendationModel.id == str(recommendation_id))
            .first()
        )
        if not db_rec:
            return None

        return Recommendation(
            id=uuid.UUID(db_rec.id),
            issue_id=uuid.UUID(db_rec.issue_id),
            evidence_ids=[uuid.uuid4()],
            content=db_rec.rationale,
            status=RecommendationStatus[db_rec.status],
        )


class LogNotificationRepository(NotificationRepository):
    """Notification implementation that logs outgoing SMS messages."""

    def notify(
        self, citizen_id: uuid.UUID, message: str, to_phone: str | None = None
    ) -> None:
        logger = _get_notification_logger()
        if hasattr(logger, "info"):
            try:
                logger.info(
                    "sms_notification_sent",
                    recipient=to_phone or "Citizen",
                    citizen_id=str(citizen_id),
                    message=message,
                )
            except Exception:
                logger.info(
                    f"[SMS Sent] Recipient: {to_phone or 'Citizen'} | Citizen ID: {citizen_id} | Message: {message}"
                )


class TwilioNotificationRepository(NotificationRepository):
    """
    Twilio SMS Notification Repository implementation.
    Dispatches real-time operational SMS messages via Twilio REST API.
    """

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_phone: str | None = None,
    ) -> None:
        self.account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.from_phone = (
            from_phone
            or os.environ.get("TWILIO_PHONE_NUMBER", "")
            or os.environ.get("TWILIO_FROM_PHONE", "+15551234567")
        )
        self.logger = _get_notification_logger()

    def notify(
        self, citizen_id: uuid.UUID, message: str, to_phone: str | None = None
    ) -> None:
        target_phone = (
            to_phone or os.environ.get("DEFAULT_CITIZEN_PHONE", "") or "+15550192834"
        )

        is_configured = (
            self.account_sid
            and self.auth_token
            and self.account_sid.startswith("AC")
            and not self.account_sid.startswith("ACXXXX")
            and not self.auth_token.startswith("your_")
        )

        if not is_configured:
            # Fallback to simulation logging when credentials are absent or placeholders
            if hasattr(self.logger, "info"):
                try:
                    self.logger.info(
                        "twilio_sms_simulated",
                        recipient=target_phone,
                        citizen_id=str(citizen_id),
                        message=message,
                        reason="Twilio credentials not set in .env",
                    )
                except Exception:
                    self.logger.info(
                        f"[Twilio SMS Simulated] Recipient: {target_phone} | Citizen ID: {citizen_id} | Message: {message}"
                    )
            return

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"

        payload_data = {
            "From": self.from_phone,
            "To": target_phone,
            "Body": message,
        }

        encoded_payload = urllib.parse.urlencode(payload_data).encode("utf-8")

        auth_string = f"{self.account_sid}:{self.auth_token}"
        auth_header = "Basic " + base64.b64encode(auth_string.encode("utf-8")).decode(
            "utf-8"
        )

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        req = urllib.request.Request(
            url, data=encoded_payload, headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                resp_body = response.read().decode("utf-8")
                if hasattr(self.logger, "info"):
                    try:
                        self.logger.info(
                            "twilio_sms_sent",
                            recipient=target_phone,
                            citizen_id=str(citizen_id),
                            message=message,
                            twilio_response=resp_body[:150],
                        )
                    except Exception:
                        self.logger.info(
                            f"[Twilio SMS Sent] Recipient: {target_phone} | Message: {message}"
                        )
        except Exception as e:
            if hasattr(self.logger, "error"):
                try:
                    self.logger.error(
                        "twilio_sms_failed",
                        recipient=target_phone,
                        citizen_id=str(citizen_id),
                        error=str(e),
                    )
                except Exception:
                    self.logger.error(f"[Twilio SMS Failed] Error: {e}")


class LogEmailRepository(EmailRepository):
    """Email repository implementation that logs outgoing email messages."""

    def send_email(
        self, to_email: str, subject: str, message: str, is_html: bool = False
    ) -> None:
        logger = _get_notification_logger()
        if hasattr(logger, "info"):
            try:
                logger.info(
                    "email_sent_simulated",
                    recipient=to_email,
                    subject=subject,
                    is_html=is_html,
                    message_snippet=message[:100],
                )
            except Exception:
                logger.info(f"[Email Simulated] To: {to_email} | Subject: {subject}")


class SMTPEmailRepository(EmailRepository):
    """
    SMTP Email Repository implementation.
    Sends emails via SMTP server (e.g. Gmail, Mailtrap, SendGrid SMTP).
    """

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_user: str | None = None,
        smtp_pass: str | None = None,
        smtp_from: str | None = None,
    ) -> None:
        self.smtp_host = smtp_host or os.environ.get("SMTP_HOST", "")
        self.smtp_port = smtp_port or int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.environ.get("SMTP_USER", "")
        self.smtp_pass = smtp_pass or os.environ.get("SMTP_PASS", "")
        self.smtp_from = (
            smtp_from
            or os.environ.get("SMTP_FROM", "")
            or "Project Helix <noreply@helix.dev>"
        )
        self.logger = _get_notification_logger()

    def send_email(
        self, to_email: str, subject: str, message: str, is_html: bool = False
    ) -> None:
        if not self.smtp_host or not self.smtp_user:
            # Fallback to simulation log
            LogEmailRepository().send_email(to_email, subject, message, is_html)
            return

        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.smtp_from
        msg["To"] = to_email

        mime_text = MIMEText(message, "html" if is_html else "plain", "utf-8")
        msg.attach(mime_text)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.starttls()
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_from, [to_email], msg.as_string())

            if hasattr(self.logger, "info"):
                try:
                    self.logger.info(
                        "email_sent_smtp",
                        recipient=to_email,
                        subject=subject,
                        smtp_host=self.smtp_host,
                    )
                except Exception:
                    self.logger.info(
                        f"[Email Sent via SMTP] To: {to_email} | Subject: {subject}"
                    )
        except Exception as e:
            if hasattr(self.logger, "error"):
                try:
                    self.logger.error(
                        "email_smtp_failed", recipient=to_email, error=str(e)
                    )
                except Exception:
                    self.logger.error(f"[Email SMTP Error] {e}")


class HTTPEmailRepository(EmailRepository):
    """
    HTTP API Email Repository implementation.
    Dispatches outbound email messages via REST / HTTP Webhook API.
    """

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        from_email: str | None = None,
    ) -> None:
        self.api_url = api_url or os.environ.get("EMAIL_API_URL", "")
        self.api_key = (
            api_key
            or os.environ.get("EMAIL_API_KEY", "")
            or os.environ.get("SENDGRID_API_KEY", "")
        )
        self.from_email = (
            from_email or os.environ.get("EMAIL_FROM", "") or "noreply@helix.dev"
        )
        self.logger = _get_notification_logger()

    def send_email(
        self, to_email: str, subject: str, message: str, is_html: bool = False
    ) -> None:
        import json

        if not self.api_url:
            # Fallback to SMTP or Log
            SMTPEmailRepository().send_email(to_email, subject, message, is_html)
            return

        payload = {
            "to": to_email,
            "subject": subject,
            "message": message,
            "is_html": is_html,
            "from": self.from_email,
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url, data=data, headers=headers, method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                resp_body = response.read().decode("utf-8")
                if hasattr(self.logger, "info"):
                    try:
                        self.logger.info(
                            "email_sent_http",
                            recipient=to_email,
                            subject=subject,
                            api_url=self.api_url,
                            response=resp_body[:150],
                        )
                    except Exception:
                        self.logger.info(
                            f"[Email Sent via HTTP API] To: {to_email} | Subject: {subject}"
                        )
        except Exception as e:
            if hasattr(self.logger, "error"):
                try:
                    self.logger.error(
                        "email_http_failed", recipient=to_email, error=str(e)
                    )
                except Exception:
                    self.logger.error(f"[Email HTTP Error] {e}")
