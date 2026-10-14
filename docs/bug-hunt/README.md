# Bug hunt, 2026-09-26

Working folder for the pre-launch reliability sweep of StoneWalker (branch `refactor/coherence-and-qr-reliability`).

| File | What it holds | Owner |
|---|---|---|
| [tasks.md](tasks.md) | The task board: F-items (bugs), A-items (accounts audit) and D-items (docs), with status and file ownership | lead |
| `findings.md` | A log of each fixed bug: root cause, fix and test (created by the fixers) | fixers |
| [sitemap.md](sitemap.md) | Every route: path, name, view, auth, methods and template. Covers i18n prefix rules, orphaned routes and templates, and dead code | docs |
| [flows.md](flows.md) | Mermaid flows derived from code: (a) stone lifecycle, (b) QR scan and email-first finder, (c) shop and Stripe, (d) premium, (e) signup, activation, reset and Discourse SSO. Ends with a list of **new suspicions** | docs |
| [pipelines.md](pipelines.md) | Tests (runner, pytest, CI, pre-push), deploy, static, translations, QR, pack PDF, certificate and email, with fragilities | docs |

## Old docs that are out of date

Treat these as history, not spec:
- `docs/wiki/features/stone-management.md` and `scanning.md`: sealing on scan, attempt-based blackout, `stone_sealed.html`, `/stonescan/`.
- `docs/CLAUDE.md`:
  - "3-day cooldown": it's actually one week, keyed on finds.
  - `/stone-link/<uuid>/` and `/regenerate-qr/`: the QR URL is now `/stone-link/<n>/?key=`, and the regenerate endpoint doesn't exist.
  - "1 unclaimed QR at a time": the cap is actually 30.
  - "header.js has two copies": the `static/` copy is collectstatic output.

Where these docs disagree with the code, flows.md and sitemap.md follow the code.
