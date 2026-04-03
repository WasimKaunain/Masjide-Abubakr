import requests
import os
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


WHATSAPP_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v22.0")

if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
    raise ValueError("WHATSAPP_TOKEN or WHATSAPP_PHONE_ID not set in environment")

WHATSAPP_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"


def _format_phone(phone: str) -> str:
    """
    Ensures phone number is:
    - Digits only
    - Prefixed with 91 if only 10 digits
    """

    digits = "".join(filter(str.isdigit, str(phone)))

    # If already 12 digits starting with 91 → OK
    if len(digits) == 12 and digits.startswith("91"):
        return digits

    # If 10 digits → add India code
    if len(digits) == 10:
        return "91" + digits

    # Otherwise return as-is (or log error)
    return digits


def send_whatsapp_reminders(
    donors: List[Dict],
    month_name: str
) -> Tuple[int, int, List[Dict]]:
    """
    Sends WhatsApp template messages to donors.

    Returns:
        sent_count, failed_count, detailed_results
    """

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    sent = 0
    failed = 0
    results = []

    for donor in donors:
        raw_phone = donor.get("phone")

        # Skip if phone is NULL or empty
        if not raw_phone:
            logger.warning(
                "Skipping donor %s due to missing phone number",
                donor.get("name")
            )
            failed += 1
            results.append({
                "phone": None,
                "status": "skipped_no_phone",
                "donor": donor.get("name")
            })
            continue

        phone = _format_phone(raw_phone)

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": "donation_reminder",
                "language": {"code": "hi"},
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
                headers=headers,
                json=payload,
                timeout=15
            )

            data = response.json()

            if response.status_code == 200:
                sent += 1
                message_id = data.get("messages", [{}])[0].get("id")

                logger.info(
                    "WhatsApp sent | phone=%s | message_id=%s",
                    phone,
                    message_id
                )

                results.append({
                    "phone": phone,
                    "status": "sent",
                    "message_id": message_id
                })

            else:
                failed += 1

                logger.error(
                    "WhatsApp failed | phone=%s | response=%s",
                    phone,
                    data
                )

                results.append({
                    "phone": phone,
                    "status": "failed",
                    "error": data
                })

        except requests.exceptions.RequestException as e:
            failed += 1
            logger.exception("Request exception for %s", phone)

            results.append({
                "phone": phone,
                "status": "exception",
                "error": str(e)
            })

    return sent, failed, results