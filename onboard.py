"""Add a dog (and its owner) to the database, then print its scan URL and save a QR.

Usage:
    python onboard.py --name "Rex" --breed "Labrador" \
        --owner-name "Jane Doe" --owner-phone "+61..." [--owner-email "..."]

There is no onboarding screen by design — dogs are added from the terminal for now.
Each run also saves a QR image of the scan URL into ./qrcodes, ready to print as the tag.
"""

import argparse
import os
import secrets
from pathlib import Path

import qrcode

from app.db import Dog, Owner, SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a dog and print its scan URL.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--breed", required=True)
    parser.add_argument("--owner-name", required=True)
    parser.add_argument("--owner-phone", required=True)
    parser.add_argument("--owner-email")
    args = parser.parse_args()

    if SessionLocal is None:
        raise SystemExit("DATABASE_URL is not set — can't reach the database.")

    with SessionLocal() as session:
        # Reuse an owner with the same name and phone; otherwise create one.
        owner = (
            session.query(Owner)
            .filter(Owner.name == args.owner_name, Owner.phone == args.owner_phone)
            .first()
        )
        if owner is None:
            owner = Owner(
                name=args.owner_name,
                phone=args.owner_phone,
                email=args.owner_email,
            )
            session.add(owner)
            session.flush()  # assigns owner.id

        token = secrets.token_urlsafe(8)
        session.add(
            Dog(
                token=token,
                name=args.name,
                breed=args.breed,
                owner_id=owner.id,
                record={},
            )
        )
        session.commit()

    base_url = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
    scan_url = f"{base_url}/d/{token}"

    # Save a QR image of the scan URL — one per dog, ready to print as the tag.
    qr_dir = Path("qrcodes")
    qr_dir.mkdir(exist_ok=True)
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in args.name) or "dog"
    qr_path = (qr_dir / f"{safe_name}-{token}.png").resolve()
    qrcode.make(scan_url).save(qr_path)

    print(f"Added {args.name} ({args.breed}). Owner: {args.owner_name}.")
    print()
    print("Scan URL:")
    print(scan_url)
    print()
    print(f"QR code saved to: {qr_path}")


if __name__ == "__main__":
    main()
