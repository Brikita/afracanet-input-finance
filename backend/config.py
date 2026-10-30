import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class Settings:
    database_url = os.getenv(
        "DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'afracanet.db'}"
    )
    payment_mode = os.getenv("PAYMENT_MODE", "mock")
    ai_mode = os.getenv("AI_MODE", "demo")
    access_code = os.getenv("DEMO_ACCESS_CODE", "afracanet-demo")
    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_secret = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_merchant = os.getenv("PAYPAL_MERCHANT_EMAIL", "")
    paypal_lender = os.getenv("PAYPAL_LENDER_EMAIL", "")
    paypal_webhook = os.getenv("PAYPAL_WEBHOOK_ID", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    sms_mode = os.getenv("SMS_MODE", "demo")
    sms_key = os.getenv("AFRICASTALKING_API_KEY", "")
    sms_sender = os.getenv("AFRICASTALKING_SENDER_ID", "")
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(
        ","
    )

    def validate(self):
        if self.sms_mode not in {"demo", "sandbox"}:
            raise RuntimeError(
                "Supported SMS modes: demo|sandbox. Real handset delivery is not enabled."
            )
        if self.sms_mode == "sandbox" and not self.sms_key:
            raise RuntimeError("SMS_MODE=sandbox requires AFRICASTALKING_API_KEY.")
        if self.payment_mode not in {"mock", "sandbox"} or self.ai_mode not in {
            "demo",
            "gemini",
        }:
            raise RuntimeError(
                "Supported modes: PAYMENT_MODE=mock|sandbox, AI_MODE=demo|gemini."
            )
        if self.payment_mode == "sandbox":
            if not all(
                [
                    self.paypal_client_id,
                    self.paypal_secret,
                    self.paypal_merchant,
                    self.paypal_lender,
                ]
            ):
                raise RuntimeError(
                    "Configure PayPal sandbox credentials and both account emails in .env."
                )
            if self.access_code == "afracanet-demo" or len(self.access_code) < 16:
                raise RuntimeError(
                    "Sandbox requires a unique DEMO_ACCESS_CODE of at least 16 characters."
                )
        if self.ai_mode == "gemini" and not self.gemini_key:
            raise RuntimeError("AI_MODE=gemini requires GEMINI_API_KEY.")


settings = Settings()
