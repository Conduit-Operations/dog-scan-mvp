# Architecture Document: Dog Tag MVP

## 1. System Overview

A single web service. It resolves a scanned code to one dog, shows either a vet view or a public view depending on who is looking, accepts edits to a dog's record, logs every edit as a change entry, and sends a confirmation email after an edit. Alongside it sits a terminal script that seeds dogs into the database and prints their scannable URL.

There is no second service, no background worker, no scheduled job, no external integration. One app, one database, one outbound email call.

## 2. Infrastructure

Hosted on Railway. Postgres is a managed Railway add-on. Nothing else is provisioned.

## 3. Technology Stack

- **Python + FastAPI** — the web service.
- **Postgres**, accessed through **SQLAlchemy** — the single source of truth for every dog record.
- **Jinja2** — server-rendered HTML pages. No frontend framework, no build step.
- **Resend** — the outbound email after an edit.
- **Railway** — hosting and Postgres.

## 4. Project Structure

```
app/
  main.py            FastAPI app + route definitions
  db.py              SQLAlchemy engine, session, table models
  email.py           the Resend call (one function)
  templates/
    landing.html     the two-door fork
    login.html       vet password entry
    vet.html         full dog record + edit form
    public.html      owner contact only
onboard.py           terminal script: add a dog, print its URL
```

This is a sketch, not a contract — the layout can move as the build lands, but new files should earn their place rather than appear speculatively.

## 5. Database Schema

Three tables. Kept deliberately small.

### owners
| column | type | notes |
|---|---|---|
| id | integer, primary key | |
| name | text | |
| phone | text | shown on the public page |
| email | text | optional |

### dogs
| column | type | notes |
|---|---|---|
| id | integer, primary key | internal only, never in a URL |
| token | text, unique | the random slug the URL is built from (see §7) |
| name | text | |
| breed | text | |
| microchip | text | stored, but **never** placed in a URL — it is the dog's real-world identity |
| owner_id | integer, foreign key → owners.id | |
| record | JSON | the clinical data (details + past visits) |
| created_at | timestamp | |

**Why `record` is a single JSON field, not normalized tables:** we do not yet know the real shape of a dog's clinical data — that is the friend's product's job to discover from actual vets. Normalizing now would be guessing. One JSON field lets the vet view render and edit arbitrary fields while the shape is still unknown. When the real shape is known, it gets promoted into columns; not before.

### events
The change log. Every edit writes one row. This table is the record's history and the source the confirmation email reads from.

| column | type | notes |
|---|---|---|
| id | integer, primary key | |
| dog_id | integer, foreign key → dogs.id | |
| type | text | `open` or `edit` |
| field | text | which field changed (null for `open`) |
| old_value | text | null for `open` |
| new_value | text | null for `open` |
| actor | text | who triggered it (`vet` or `public`) |
| created_at | timestamp | |

`open` events are written but never emailed (see §9). `edit` events are written and then emailed.

## 6. Configuration (env vars)

- `DATABASE_URL` — provided by Railway.
- `RESEND_API_KEY` — for the outbound email.
- `VET_PASSWORD` — the single shared password standing in for real vet accounts.
- `NOTIFICATION_EMAIL` — where edit confirmations are sent.
- `BASE_URL` — used by `onboard.py` to build the printable scan URL.

## 7. The Token And How A Scan Resolves

The tag encodes a URL ending in a token: a short, random, URL-safe slug (generated at onboarding with Python's `secrets`). It is unguessable enough that someone can't enumerate other dogs by editing the URL, but it is not a secret-grade credential — it is an address, not a password.

The token is the *only* thing tied to the dog in the URL. The internal `id` and the `microchip` never appear there. A scan is a plain web request to that URL; resolving it is a single lookup of `dogs` by `token`.

## 8. Routes

| route | does |
|---|---|
| `GET /d/{token}` | resolve the token to a dog; write an `open` event; show `landing.html` (the two-door fork). Unknown token → friendly "we don't recognise this tag" page, not an error. |
| `GET /d/{token}/vet` | the full clinical record + edit form. Requires a vet session (see §9); without one, redirect to login. |
| `GET /d/{token}/public` | owner contact only. Reads **only** the owner fields, never `record`. |
| `GET /login` / `POST /login` | vet enters `VET_PASSWORD`; on success, set the session cookie; redirect back to the vet view. |
| `POST /d/{token}/edit` | the edit path (see §9). Requires a vet session. |

## 9. The Vet/Public Fork, The Session, And The Edit Path

**The fork.** The landing route does not decide the view by itself — it offers both doors. The vet door leads through login; the public door leads straight to the contact page. What gates the *clinical* view is the presence of a valid vet session, nothing else.

**The session.** Login compares the submitted password to `VET_PASSWORD`. On success it sets a signed cookie valid for 8 hours (mirroring the pattern proven in the variation project's operator dashboard). No accounts, no roles — presence of the cookie *is* "is a vet."

**The edit path — write first, email after, never block on email.** When a vet saves an edit:

1. Write the new value into the dog's `record`.
2. Write an `edit` event row (field, old, new, actor, timestamp).
3. *Then* attempt the Resend email. If it fails, log it and move on — the save already succeeded.

This ordering is deliberate and is the inverse of the variation project's head-contractor email, which is email-*first*, commit-on-success because a legal claim must not be marked sent unless the email provably went. Here the opposite is correct: the record edit is what matters, the email is a courtesy, and a broken inbox must never cost a vet their save. This is the architectural form of the CLAUDE.md rule that the loop is never blocked by the email.

## 10. The Onboarding Script

`python onboard.py --name "Rex" --breed "Labrador" --owner-name "Jane Doe" --owner-phone "+61..." [--owner-email "..."]`

It creates the owner (or reuses one), creates the dog, generates the unique `token`, and prints the full scan URL (`BASE_URL` + `/d/` + token) so it can be turned into a QR code by hand. No onboarding screen exists yet, by design (PRD §5).

## 11. Invariants

The technical rules that hold across the build. These are the mechanism behind the CLAUDE.md behaviours and the PRD's three ideas.

- **The email never blocks a save.** Write the record and the event first; the email is best-effort.
- **The token is the only dog reference in any URL.** Never the internal `id`, never the `microchip`.
- **The public view never reads `record`.** It touches owner-contact fields only. Medical data has no path to a non-vet.
- **Migrations are additive.** Once a real dog exists in the database, no dropping tables or columns — add, with sensible defaults.
- **The record's shape stays JSON until its real shape is known.** Promoting fields to columns is a deliberate later decision, not a default.
