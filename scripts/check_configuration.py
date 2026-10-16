"""Print configuration presence and validation errors, never credential values."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.config import settings

print("Payment mode:", settings.payment_mode)
print("Assistant mode:", settings.ai_mode)
print("SMS mode:", settings.sms_mode)
for label, present in [
    ("PayPal supplier client ID", bool(settings.paypal_client_id)),
    ("PayPal supplier secret", bool(settings.paypal_secret)),
    ("Supplier sandbox email", bool(settings.paypal_merchant)),
    ("Lender sandbox email", bool(settings.paypal_lender)),
    ("PayPal webhook ID", bool(settings.paypal_webhook)),
    ("Gemini API key", bool(settings.gemini_key)),
    ("Africa's Talking sandbox API key", bool(settings.sms_key)),
    ("Unique demo code", settings.access_code != "afracanet-demo" and len(settings.access_code) >= 16),
]:
    print(label + ":", "configured" if present else "not configured")
try:
    settings.validate()
except RuntimeError as exc:
    print("Configuration error:", str(exc))
    sys.exit(1)
print("Selected modes are valid. Live external-service verification is a separate check.")
