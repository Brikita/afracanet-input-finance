"""Africa's Talking sandbox adapter; acceptance never means handset delivery."""

import httpx

from ..config import settings


def sandbox_send(phone, body):
    try:
        with httpx.Client(timeout=20) as client:
            response = client.post(
                "https://api.sandbox.africastalking.com/version1/messaging",
                headers={"apiKey": settings.sms_key, "Accept": "application/json"},
                data={
                    "username": "sandbox",
                    "to": phone,
                    "message": body,
                    "bulkSMSMode": 1,
                    **({"from": settings.sms_sender} if settings.sms_sender else {}),
                },
            )
        response.raise_for_status()
        recipients = response.json()["SMSMessageData"]["Recipients"]
        if len(recipients) != 1 or recipients[0]["number"] != phone:
            return (
                "UNCERTAIN",
                None,
                "Unexpected provider recipient response. Review the sandbox dashboard.",
            )
        recipient = recipients[0]
        if recipient.get("statusCode") != 101:
            return (
                "REJECTED",
                None,
                "Provider rejected the message. Review configuration before a new send.",
            )
        if (
            not isinstance(recipient.get("messageId"), str)
            or not recipient["messageId"]
        ):
            return (
                "UNCERTAIN",
                None,
                "Provider acceptance reference missing. Do not retry automatically.",
            )
        return (
            "ACCEPTED",
            recipient["messageId"],
            "Accepted by the sandbox gateway; this is not handset delivery.",
        )
    except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError):
        return (
            "UNCERTAIN",
            None,
            "The send outcome could not be confirmed. Review provider records before another send.",
        )
