# Lead Capture System — Build Tracker

## Overview
Backend + static hosting layer that wraps a colleague's JS form, captures leads, sends results emails, and logs everything. Deployed on Render free tier for a late-May presentation.

**Form status:** Placeholder in place. Drop colleague's files into `static/form/` and wire the submit handler to `POST /submit`. No other code changes needed.

---

## Architecture
```
QR Code → Render (static) → JS Form → POST /submit → FastAPI
                                                    ├── SQLite (submissions.db)
                                                    ├── Resend (transactional email)
                                                    └── IP enrichment (post-event batch, not hot path)
```

**Submission contract** (form must POST this shape):
```json
{
  "email": "user@example.com",
  "form_data": {},          // opaque — any shape, stored as JSON blob
  "form_version": "1.0",    // optional, defaults to "unknown"
  "is_test": false          // warm-up submissions set this true
}
```

---

## Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/submit` | Receive form, enrich, store, send email |
| GET | `/health` | Liveness check / warm-up ping |
| GET | `/export?key=SECRET` | Download clean lead CSV (excludes test submissions) |

---

## Environment Variables (`.env`)
```
RESEND_API_KEY=
EXPORT_SECRET=
FROM_EMAIL=noreply@yourdomain.com
BCC_EMAIL=yourfirm@yourdomain.com
```

---

## To-Do List

### Phase 1 — Backend Skeleton
- [x] Project structure created (`lead-capture/`)
- [x] `BUILD.md` created
- [ ] `main.py` — FastAPI app with `/submit`, `/health`, `/export`
- [ ] `models.py` — Pydantic schema
- [ ] `db.py` — SQLite setup and queries
- [ ] `requirements.txt` + `.env.example`

### Phase 2 — Email Pipeline
- [ ] `email_service.py` — Resend integration
- [ ] `templates/result_email.html` — Generic Jinja2 template (table dump of form_data)
- [ ] End-to-end test via curl

### Phase 3 — Deploy + QR
- [ ] Push to Render, confirm `/health` returns OK
- [ ] `generate_qr.py` — QR pointing at `/form/` path
- [ ] Keep-alive strategy (cron-job.org ping every 10min day-of)

### Phase 4 — Form Drop-In (when colleague delivers)
- [ ] Drop JS form files into `static/form/`
- [ ] Wire form submit handler to `POST /submit`
- [ ] Update `result_email.html` with real result fields

### Phase 5 — Day-Of Hardening
- [ ] Dummy submission warm-up test
- [ ] Export dry-run (confirm CSV is clean)
- [ ] Final README day-of checklist review

---

## Open Decisions
1. **Form integration method** — How does colleague's form handle submission? (POST to URL vs JS function call?) Determines the wiring approach.
2. **Email content** — What does the results email show? Colleague defines "the result."
3. **Audience size** — SQLite is fine to ~1000. Larger → swap to PostgreSQL (same schema).

---

## Day-Of Checklist
1. Confirm Render service is live: `GET /health` returns `{"status": "ok"}`
2. Submit a dummy form entry (`is_test: true`) 1-2 min before QR goes on screen — verify email arrives
3. QR code slide goes live
4. After presentation: `GET /export?key=<EXPORT_SECRET>` → download lead CSV

---

## Keep-Alive Note
Render free tier cold-starts can take **50+ seconds**. Set up a cron-job.org ping to `GET /health` every 10 minutes on presentation day. Don't rely on warm-up submission alone.
