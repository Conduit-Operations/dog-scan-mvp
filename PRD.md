# Product Requirements Document: Dog Tag MVP

## 1. The Problem, And What This Build Actually Is

A dog's medical history is scattered across every clinic it has ever visited. When a dog turns up at a new vet, that vet can't see what happened elsewhere — so the history gets reconstructed by phone calls, faxes, and paper passed between clinics. The idea being explored is a scannable tag on the dog's collar that opens its record on any vet's phone, with the record following the dog rather than living trapped in one clinic's filing system.

**This build is not that product.** It is the smallest working version of the product's core mechanic, built to learn how it hangs together: scan a code, open a dog's record, edit it, get told the record changed. One imaginary clinic, a handful of made-up dogs, a printed QR code. Everything real — actual clinic software, real vet accounts, physical hardware, more than one clinic — is deliberately absent.

The measure of success is not features. It is whether the loop works end to end and is understood: **scan → see the record → edit it → be notified it changed.**

## 2. The Three Ideas This Rests On

Everything below serves three distinctions. Collapsing any two of them breaks the product.

1. **Identity is not the record.** The tag carries only a pointer — *which dog this is* — never the medical history itself. The history is too large, too sensitive, and too often updated to live on a collar.

2. **The record lives in one central place, not on the tag.** This is the whole reason a second clinic can see what a first clinic wrote: the edit was saved centrally, not onto the physical object. If the data rode on the tag, edits would be stranded wherever the tag happened to be, and a lost tag would mean a lost history. Central storage is what makes the record portable.

3. **The same scan resolves differently depending on who is looking.** A logged-in vet sees the full clinical record. Anyone else — a stranger who finds a lost dog — sees only how to contact the owner, and nothing medical. One code, two outcomes, decided by who is holding the phone.

## 3. What The System Does

1. Resolves a scanned code to exactly one dog.
2. Presents a choice on landing: continue as a vet (with a login), or "I'm not a vet — whose dog is this?"
3. Lets a vet log in. A single shared password stands in for real vet accounts for now.
4. Shows a logged-in vet the dog's full record — its details and its past visits.
5. Lets a logged-in vet edit a field of the record and save it.
6. Records every edit as a change entry — what changed, from what, to what, and when — kept as the record's history.
7. Sends an email after an edit, confirming the change in plain language.
8. Shows a non-vet only the owner's contact details, with no medical information.
9. Lets the operator add a new dog by running a simple terminal command. There is no onboarding screen yet, and that is intentional.

## 4. How It's Used

### The vet's flow
1. A dog comes in. The vet scans the tag on its collar with a phone.
2. The landing page offers the two doors; the vet takes the "continue as a vet" door and logs in.
3. The dog's full record opens — details and past visits, read from the central record, not from the tag.
4. After treating the dog, the vet edits a field (for example, updates the weight or adds a note) and saves.
5. The page shows the updated record. Shortly after, an email arrives confirming exactly what changed.
6. The next time this dog is scanned — even much later, even by a different vet — the record already shows that change, because it was saved centrally.

### The stranger's flow
1. Someone finds a lost dog and scans the tag out of curiosity or concern.
2. The landing page offers the two doors; with no vet login, they take the "I'm not a vet" door.
3. They see how to contact the owner — and nothing about the dog's health.

## 5. Out Of Scope

These are excluded on purpose. Each has a reason, and the reason is what matters when deciding later whether to revisit it.

**Belongs to the friend's real product, not this learning build:**
- Any connection to real clinic software.
- Physical hardware. The "tag" is a printed QR code; nothing is manufactured.
- Support for more than one clinic, or anything that assumes multiple clinics exist.

**Needs real infrastructure this build deliberately fakes:**
- Real vet accounts, roles, or proper authentication. A single shared password is the stand-in, and that is the ceiling.
- A polished way for owners to be contacted — masked numbers, a "notify the owner" relay, or any messaging. The public page shows a contact and stops there.

**Genuinely useful later, but not part of proving the loop:**
- An onboarding screen. Dogs are added from the terminal for now.
- Reporting, analytics, charts, or any dashboard beyond the single dog record.
- Anything that lets a non-vet see or infer medical information.

If a request crosses one of these lines, it should be raised and decided deliberately, not absorbed quietly.

## 6. What This Is A Slice Of

The larger idea — a medical passport that follows a dog across every clinic, syncing with whatever software each clinic runs, gating who sees what — is real, but it is not being built here and should not be specified here. This document covers only the loop. The grand vision stays a single paragraph on purpose, so that every request can be measured against the loop rather than against an unbuilt product.
