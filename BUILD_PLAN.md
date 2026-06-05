# Build Plan: Dog Tag MVP

Reference `PRD.md` for what the product does and why. Reference `ARCHITECTURE.md` for how each piece is built — schema, routes, the edit path. Each phase below points to those files rather than repeating them.

## Current Build Status — Phase 0 complete

The foundation is live: the app deploys on Railway, Postgres is connected, the three tables exist, and the health check returns OK with the database reachable. Building the loop: scan → see the record → edit → get notified. **On Phase 1** — onboard a dog and resolve a scan.

There is no Version History table and no HISTORY.md yet — both arrive when there's a second version to track and completed work to archive.

## How To Read A Phase

Each phase is a coherent step that ends in something testable on a phone or in an inbox — never "run the tests." Build them in order; each unblocks the next. A phase names *what* to build and *where the detail lives*; it does not re-specify the schema or routes (those are in ARCHITECTURE).

## Phases

### Phase 0 — Foundation
Stand up the skeleton. FastAPI app boots and deploys on Railway; Postgres connected; the three tables created (ARCHITECTURE §5); a health check route responds.

**Test:** the deployed URL's health check returns OK, and the database is reachable. Nothing visible to a user yet — this just proves the ground is solid.

**Status: ✅ Done.** Deployed on Railway; `/health` returns OK with the database connected.

### Phase 1 — Onboard a dog, resolve a scan
The terminal script creates a dog and prints its scan URL (ARCHITECTURE §10). Visiting `/d/{token}` resolves the token and shows a bare page with the dog's name (ARCHITECTURE §7–§8). An unknown token shows the friendly "we don't recognise this tag" page, not an error.

**Test:** run `onboard.py` for a test dog (Rex), open the printed URL on a phone, see Rex's name. Then change the URL to a made-up token and confirm the friendly not-found page appears.

### Phase 2 — The fork and the public door
The landing page offers the two doors (ARCHITECTURE §8). The public door opens a page showing the owner's contact details only — and nothing medical anywhere on it (ARCHITECTURE §9; this is the PRD §2 third idea made real).

**Test:** from the landing page, take the "I'm not a vet" door; confirm you see the owner's phone and *no* clinical information.

### Phase 3 — Vet login and the record (read-only)
Login with the shared password sets the 8-hour session cookie (ARCHITECTURE §9). The vet door opens the full record to read. Visiting the vet view without a session redirects to login.

**Test:** take the vet door, enter the password, see the full record. Then open the vet view in a fresh browser with no session and confirm you're redirected to login.

### Phase 4 — Edit and log
The vet view gains an edit form. Saving writes the new value into the dog's record and writes an `edit` event — what changed, from what, to what (ARCHITECTURE §9, steps 1–2).

**Test:** edit a field (say the weight), reload the page, and confirm the new value persists.

### Phase 5 — Email on edit
Wire Resend. After a successful save, send the confirmation email naming the change, in plain language (ARCHITECTURE §9, step 3). The email is best-effort and must never block the save.

**Test:** edit a field and confirm an email arrives within a minute describing the change. Then, to prove the loop-protection invariant (ARCHITECTURE §11), temporarily break `RESEND_API_KEY` and confirm the save *still* succeeds — only the email is missing.

### Phase 6 — Open-event logging and polish
Write an `open` event each time a tag is scanned (ARCHITECTURE §5, §8) — logged, never emailed. Tidy any rough edges surfaced while testing the earlier phases.

**Test:** scan a tag, then confirm (via a quick database look or a temporary readout) that an `open` event was recorded and that no email was sent for it.

## After The Loop

Once the loop works end to end, the next step is *not* automatically more features — it's deciding whether the loop taught what it needed to. The parked themes, all documented as out-of-scope in PRD §5, are the horizon when the time comes: real vet accounts and authentication, a connection to real clinic software, an owner-notification relay, and support for more than one clinic. None of these get planned here until a concrete reason to build them surfaces.
