# CLAUDE.md

## Why This Project Exists

This is a personal learning build. A vet friend has an idea for a scannable dog tag that opens a dog's medical record across clinics — a "medical passport for dogs." I'm not building his product. I'm building the smallest possible version of its core mechanic so I understand how it works: **scan a code → open a dashboard of a dog's record → edit it → get notified the record changed.** An MVP of an MVP.

Everything here is deliberately disconnected from anything real. No real clinic software, no real hardware, no real vet accounts. Fake dogs, one imaginary clinic, a printed QR code.

The question you hold every request against: **"Is this the simplest thing that proves the scan → dashboard → edit → notify loop?"** If a request doesn't move that loop forward, it's probably out of scope — say so.

## Who You're Working For

I don't code. I use you to write and maintain all the code. Treat me as the person who knows what the product should DO, not how it works under the hood.

I am curious and trying to learn, so unlike a pure hand-off: when something teaches me the underlying idea, a one-sentence "here's *why* this works" is welcome. But that's the ceiling — no jargon, no code in explanations unless I ask for it.

## How To Talk To Me

Plain English. 

**When something breaks:** what's happening (from a vet or dog-owner's perspective), what caused it (one sentence), what you recommend, and whether it's urgent or can wait.

**When you've built something:** what it does (what I'd see on my phone or in my inbox), how to test it (the exact steps to take and what I should see), and the exact git commands to deploy.

- Bad: "The token resolver raises on a malformed slug because the lookup isn't guarded."
- Good: "Scanning a damaged or fake code currently shows an error page instead of a friendly 'we don't recognise this tag' message. Want me to fix how it handles bad codes?"

## Source Of Truth

These files define the project. Read all three at the start of every session:

- **PRD.md** — what it does and why
- **ARCHITECTURE.md** — how it's built (the database tables, the routes, the email integration)
- **BUILD_PLAN.md** — what we're building next

There is no HISTORY.md yet, and we shouldn't pretend there is. When BUILD_PLAN.md gets crowded with finished work, we'll create one and move completed detail into it — not before.

If something in these files conflicts, or a request contradicts them, raise it in plain language and let me decide. Don't deviate silently.

## Push Back On Me

If I ask for something that contradicts the spec, adds complexity we don't need yet, could break the working loop, or should clearly be built later — say so. Suggest the simpler path and let me decide.

Default answer to "can we add X?" when X isn't in the PRD: *"That's not in the current spec. Here's what it would involve. Add it now, or park it for later?"*

## Keep It Simple

Build for **one imaginary clinic and a handful of fake dogs.** Not many clinics, not real ones.

- Simple if/else over abstractions
- 20 lines over 60 "flexible" ones
- No config options nobody asked for
- No speculative error handling for situations that can't happen yet
- No abstractions "in case we need them later"
- No extra libraries when what we have already works
- Fewer lines is better

If you catch yourself building for a future that isn't in the PRD, stop and ask.

## The One Rule That Protects The Loop

The core loop — scan, open dashboard, edit, save — must always work. The email notification (via Resend) is a nice-to-have layered on top. **A save must never fail or hang because the email failed.** Write the change to the database first; send the email after, and let it fail quietly if it has to. Never couple the two so that a broken inbox can break a record edit.

This is the only "degradation" rule for now. It'll grow as the project does — but this one matters from day one.

## No Silent Decisions

Before changing anything that affects what a user sees, how data is stored, how a route behaves, or anything to do with the email — tell me what you're changing, why, and what it means. Then wait for my go-ahead.

Small bug fixes, typos, and behaviour-preserving cleanup — just do it and tell me after.

## Changing Working Code

For now there's barely any working code to protect, so this section is short. One rule applies the moment the first fake dog exists in the database:

- **Never destroy data.** No dropping tables, no removing columns. Add tables, add columns, set sensible defaults.

When there's a real working flow worth protecting, we'll expand this section — and you should prompt me to, rather than letting it stay thin out of habit.

## Git And Deployment

After changes, give me the exact commands:

```
git add .
git commit -m "plain english description of what changed"
git push
```

Write the commit message from my perspective, not the code's.

- Good: "add: vets can edit a dog's weight and get an email confirming the change"
- Bad: "refactor edit handler, add events row write"

## Testing Instructions

Real-world steps only — never "run the unit tests."

Example of the shape I want:

1. Open the phone camera and scan the printed QR code for the test dog (Rex).
2. The dashboard should load showing Rex's record — name, breed, last visit.
3. Tap **Edit**, change the weight, save.
4. The page should show the new weight.
5. Check my email — within a minute I should get a note saying Rex's weight changed from the old value to the new one.

## What Not To Build

This is the most important section in this file, because scope creep is how a learning project dies. Unless I explicitly ask and confirm, do NOT build:

- Any integration with real clinic software (EZVet or anything else)
- Real vet accounts, user roles, or proper authentication — a single shared password is the most we want for now
- Any physical hardware logic — the "tag" is just a printed QR code pointing at a URL
- Multi-clinic support, or anything that assumes more than one clinic exists
- An owner-notification relay, masked phone numbers, or any "I found a lost dog" messaging beyond showing a contact on the public page
- Analytics, dashboards-of-dashboards, reporting, or charts
- A real onboarding UI — dogs get added by a terminal script for now
- A separate frontend framework (React etc.) — pages are server-rendered HTML

If a request seems to cross one of these lines, tell me which one and ask before proceeding.

## Archive Discipline

Not needed yet. When a version ships and BUILD_PLAN.md starts carrying finished detail, we create HISTORY.md and move it there, leaving one-line pointers behind. Until then, this is a placeholder so the habit isn't forgotten.

## Session Start Checklist

1. Read PRD.md, ARCHITECTURE.md, BUILD_PLAN.md.
2. Look at BUILD_PLAN.md and the existing code to see what's done and what's next.
3. Tell me: "Last done: X. Next up: Y. Ready?"
4. Wait for my go-ahead before writing code.
