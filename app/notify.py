import json
import os
import urllib.request

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "")

# Resend's shared test sender. Swap for an address on a verified domain later.
FROM_ADDRESS = "onboarding@resend.dev"


def build_message(dog_name, changes):
    """Plain-language summary of an edit, one line per changed field."""
    lines = [f"{dog_name}'s record was updated by a vet:", ""]
    for field, old, new in changes:
        lines.append(f'- {field} changed from "{old}" to "{new}"')
    return "\n".join(lines)


def send_edit_email(dog_name, changes):
    """Best-effort confirmation to NOTIFICATION_EMAIL. Never raises — a broken
    inbox must never cost a vet their save, which has already happened."""
    if not RESEND_API_KEY or not NOTIFICATION_EMAIL:
        return
    payload = {
        "from": FROM_ADDRESS,
        "to": [NOTIFICATION_EMAIL],
        "subject": f"{dog_name}'s record was updated",
        "text": build_message(dog_name, changes),
    }
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10):
            pass
    except Exception as exc:
        # Log and move on. The save is already safe.
        print(f"[notify] edit email failed (save was unaffected): {exc}")
