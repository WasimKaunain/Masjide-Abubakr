import requests
import os
import logging

logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID")

WHATSAPP_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}


def send_whatsapp_reminders(donors, month_name):
    sent = 0
    failed = 0

    for donor in donors:
        payload = {
            "messaging_product": "whatsapp",
            "to": donor["phone"],
            "type": "template",
            "template": {
                "name": "donation_reminder",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": donor["name"]},
                            {"type": "text", "text": str(donor["amount"])},
                            {"type": "text", "text": month_name}
                        ]
                    }
                ]
            }
        }

        try:
            response = requests.post(
                WHATSAPP_URL,
                headers=HEADERS,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                sent += 1
                logger.info("WhatsApp sent to %s", donor["phone"])
            else:
                failed += 1
                logger.error(
                    "WhatsApp failed for %s | %s",
                    donor["phone"],
                    response.text
                )

        except Exception as e:
            failed += 1
            logger.exception("Exception for %s", donor["phone"])

    return sent, failed
